from __future__ import annotations
import json, hashlib
from .config import settings

LOCAL_MEMORY = settings.data_dir / "workflow_memory.jsonl"

class WorkflowMemory:
    def __init__(self):
        self.backend = "local-jsonl"
        self.pc = None
        self.index = None

        if settings.use_pinecone and settings.pinecone_api_key:
            try:
                from pinecone import Pinecone, ServerlessSpec

                self.pc = Pinecone(api_key=settings.pinecone_api_key)
                names = [item.name for item in self.pc.list_indexes()]

                if settings.pinecone_index not in names:
                    self.pc.create_index(
                        name=settings.pinecone_index,
                        dimension=1024,
                        metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                    )

                self.index = self.pc.Index(settings.pinecone_index)
                self.backend = "pinecone"

            except Exception as exc:
                print(f"[memory] Pinecone unavailable; using local memory: {exc}")

    def _records(self):
        if not LOCAL_MEMORY.exists():
            return []

        output = []
        for line in LOCAL_MEMORY.read_text(encoding="utf-8").splitlines():
            try:
                output.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return output

    def search(self, query: str, limit: int = 3) -> list[str]:
        if self.backend == "pinecone" and self.pc and self.index:
            try:
                embedding = self.pc.inference.embed(
                    model="llama-text-embed-v2",
                    inputs=[query],
                    parameters={"input_type": "query", "truncate": "END"},
                )
                result = self.index.query(
                    vector=embedding[0]["values"],
                    top_k=limit,
                    include_metadata=True,
                )
                return [
                    match["metadata"].get("text", "")
                    for match in result.get("matches", [])
                    if match.get("metadata")
                ]
            except Exception as exc:
                print(f"[memory] Pinecone search fallback: {exc}")

        query_words = set(query.lower().split())
        rows = sorted(
            self._records(),
            key=lambda row: len(
                query_words & set(row.get("text", "").lower().split())
            ),
            reverse=True,
        )
        return [row.get("text", "") for row in rows[:limit] if row.get("text")]

    def store(self, workflow_id: str, text: str, metadata: dict | None = None):
        metadata = metadata or {}

        if self.backend == "pinecone" and self.pc and self.index:
            try:
                embedding = self.pc.inference.embed(
                    model="llama-text-embed-v2",
                    inputs=[text],
                    parameters={"input_type": "passage", "truncate": "END"},
                )
                vector_id = hashlib.sha256(
                    f"{workflow_id}:{text}".encode()
                ).hexdigest()[:32]

                self.index.upsert(
                    vectors=[
                        {
                            "id": vector_id,
                            "values": embedding[0]["values"],
                            "metadata": {"text": text, **metadata},
                        }
                    ]
                )
                return

            except Exception as exc:
                print(f"[memory] Pinecone store fallback: {exc}")

        with LOCAL_MEMORY.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    {
                        "workflow_id": workflow_id,
                        "text": text,
                        "metadata": metadata,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

memory = WorkflowMemory()
