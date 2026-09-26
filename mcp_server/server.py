from datetime import datetime, timezone
from fastmcp import FastMCP

mcp = FastMCP("Workflow Operations Tools")

@mcp.tool
def calculate(expression: str) -> str:
    """Evaluate a basic arithmetic expression."""
    allowed = set("0123456789.+-*/() ")
    if not expression or any(char not in allowed for char in expression):
        raise ValueError("Only basic arithmetic expressions are allowed.")
    return str(eval(expression, {"__builtins__": {}}, {}))

@mcp.tool
def current_utc_time() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()

@mcp.tool
def risk_matrix(likelihood: int, impact: int) -> dict:
    """Calculate a 1-5 x 1-5 operational risk score."""
    if likelihood not in range(1, 6) or impact not in range(1, 6):
        raise ValueError("likelihood and impact must be integers from 1 to 5.")

    score = likelihood * impact

    if score >= 16:
        level = "critical"
    elif score >= 10:
        level = "high"
    elif score >= 5:
        level = "medium"
    else:
        level = "low"

    return {
        "likelihood": likelihood,
        "impact": impact,
        "score": score,
        "level": level,
    }

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=9000,
    )
