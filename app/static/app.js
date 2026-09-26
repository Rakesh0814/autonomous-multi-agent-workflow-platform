const runButton =
  document.getElementById("run");

const goalInput =
  document.getElementById("goal");

const exampleButton =
  document.getElementById("exampleBtn");

const statusElement =
  document.getElementById("status");

const statusDot =
  document.getElementById("statusDot");

const workflowId =
  document.getElementById("workflowId");

const memoryBackend =
  document.getElementById("memoryBackend");

const crewStatus =
  document.getElementById("crewStatus");

const n8nStatus =
  document.getElementById("n8nStatus");

const planCard =
  document.getElementById("plan-card");

const agentsCard =
  document.getElementById("agents-card");

const reportCard =
  document.getElementById("report-card");

const planElement =
  document.getElementById("plan");

const agentResultsElement =
  document.getElementById(
    "agent-results"
  );

const reportElement =
  document.getElementById("report");

const executiveSummary =
  document.getElementById(
    "executiveSummary"
  );

const keyFindings =
  document.getElementById(
    "keyFindings"
  );

const actions =
  document.getElementById("actions");

const recommendation =
  document.getElementById(
    "recommendation"
  );


const exampleGoal = `
Analyze why customer support resolution time may have increased over the last quarter.

Identify likely operational causes, key risks and dependencies, and produce a prioritized 30-day improvement plan with measurable actions.
`.trim();


exampleButton.addEventListener(
  "click",
  () => {
    goalInput.value =
      exampleGoal;

    goalInput.focus();
  }
);


function escapeHtml(value) {

  return String(value ?? "")
    .replaceAll(
      "&",
      "&amp;"
    )
    .replaceAll(
      "<",
      "&lt;"
    )
    .replaceAll(
      ">",
      "&gt;"
    )
    .replaceAll(
      '"',
      "&quot;"
    )
    .replaceAll(
      "'",
      "&#039;"
    );
}


function setStatus(
  text,
  mode
) {

  statusElement.textContent =
    text;

  statusDot.className =
    "status-dot";

  if (mode === "running") {

    statusDot.classList.add(
      "running-dot"
    );

  } else if (
    mode === "completed"
  ) {

    statusDot.classList.add(
      "success-dot"
    );

  } else if (
    mode === "failed"
  ) {

    statusDot.classList.add(
      "failed-dot"
    );

  } else {

    statusDot.classList.add(
      "idle-dot"
    );
  }
}


function resetResults() {

  planCard.classList.add(
    "hidden"
  );

  agentsCard.classList.add(
    "hidden"
  );

  reportCard.classList.add(
    "hidden"
  );

  planElement.innerHTML = "";

  agentResultsElement.innerHTML =
    "";

  reportElement.textContent = "";

  executiveSummary.innerHTML = "";

  keyFindings.innerHTML = "";

  actions.innerHTML = "";

  recommendation.innerHTML = "";
}


function formatAgentName(
  agent
) {

  const names = {

    researcher:
      "Research Agent",

    analyst:
      "Analysis Agent",

    operations:
      "Operations Agent",

    reviewer:
      "Reviewer Agent"
  };

  return (
    names[agent] ||
    `${agent} Agent`
  );
}


function renderPlan(plan) {

  planElement.innerHTML =
    plan
      .map(
        (
          item,
          index
        ) => {

          return `
            <div class="plan-item">

              <span class="plan-item-agent">
                ${index + 1}
                ·
                ${escapeHtml(
                  formatAgentName(
                    item.agent
                  )
                )}
              </span>

              <p>
                ${escapeHtml(
                  item.task
                )}
              </p>

            </div>
          `;
        }
      )
      .join("");

  planCard.classList.remove(
    "hidden"
  );
}


function renderAgentResults(
  results
) {

  agentResultsElement.innerHTML =
    results
      .map(
        (item) => {

          return `
            <article
              class="agent-output-card"
            >

              <h3>
                ${escapeHtml(
                  formatAgentName(
                    item.agent
                  )
                )}
              </h3>

              <div class="agent-task">
                ${escapeHtml(
                  item.task
                )}
              </div>

              <pre>${escapeHtml(
                item.output
              )}</pre>

            </article>
          `;
        }
      )
      .join("");

  agentsCard.classList.remove(
    "hidden"
  );
}


function findSection(
  report,
  heading,
  nextHeadings
) {

  const lower =
    report.toLowerCase();

  const start =
    lower.indexOf(
      heading.toLowerCase()
    );

  if (start === -1) {

    return "";
  }

  let contentStart =
    start +
    heading.length;

  const remaining =
    lower.slice(
      contentStart
    );

  let nearestEnd =
    report.length;

  for (
    const nextHeading
    of nextHeadings
  ) {

    const position =
      remaining.indexOf(
        nextHeading
          .toLowerCase()
      );

    if (
      position !== -1
      &&
      contentStart
        +
        position
        <
        nearestEnd
    ) {

      nearestEnd =
        contentStart
        +
        position;
    }
  }

  return report
    .slice(
      contentStart,
      nearestEnd
    )
    .replace(
      /^[:\s#*\d.\-]+/,
      ""
    )
    .trim();
}


function textToHtml(
  text
) {

  if (!text) {

    return `
      <p>
        See full reviewed report below.
      </p>
    `;
  }

  const lines =
    text
      .split("\n")
      .map(
        line =>
          line.trim()
      )
      .filter(Boolean);

  if (
    lines.some(
      line =>
        line.startsWith("-")
        ||
        line.startsWith("•")
        ||
        /^\d+\./.test(line)
    )
  ) {

    const items =
      lines.map(
        line =>
          line
            .replace(
              /^[-•]\s*/,
              ""
            )
            .replace(
              /^\d+\.\s*/,
              ""
            )
      );

    return `
      <ul>
        ${items
          .map(
            item =>
              `<li>${escapeHtml(item)}</li>`
          )
          .join("")}
      </ul>
    `;
  }

  return `
    <p>
      ${escapeHtml(
        text
      )}
    </p>
  `;
}


function renderReport(
  report
) {

  reportElement.textContent =
    report;


  const summary =
    findSection(
      report,
      "Executive Summary",
      [
        "Key Findings",
        "Risks / Dependencies",
        "Recommended Actions",
        "Next Steps"
      ]
    );


  const findings =
    findSection(
      report,
      "Key Findings",
      [
        "Risks / Dependencies",
        "Recommended Actions",
        "Next Steps"
      ]
    );


  const recommendations =
    findSection(
      report,
      "Recommended Actions",
      [
        "Next Steps"
      ]
    );


  const nextSteps =
    findSection(
      report,
      "Next Steps",
      []
    );


  executiveSummary.innerHTML =
    textToHtml(
      summary
    );


  keyFindings.innerHTML =
    textToHtml(
      findings
    );


  actions.innerHTML =
    textToHtml(
      recommendations
    );


  recommendation.innerHTML =
    textToHtml(
      nextSteps
      ||
      recommendations
    );


  reportCard.classList.remove(
    "hidden"
  );


  reportCard.scrollIntoView({
    behavior: "smooth",
    block: "start"
  });
}


async function runWorkflow() {

  const goal =
    goalInput
      .value
      .trim();


  if (!goal) {

    goalInput.focus();

    return;
  }


  runButton.disabled =
    true;


  runButton.innerHTML =
    `
      <span>
        ◌
      </span>
      Running workflow...
    `;


  resetResults();


  setStatus(
    "Running",
    "running"
  );


  workflowId.textContent =
    "Creating...";


  try {

    const response =
      await fetch(
        "/api/workflow/run",
        {
          method:
            "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body:
            JSON.stringify({
              goal
            })
        }
      );


    const data =
      await response.json();


    if (!response.ok) {

      throw new Error(
        data.detail
        ||
        "Workflow execution failed."
      );
    }


    workflowId.textContent =
      data.workflow_id;


    memoryBackend.textContent =
      data.memory_backend;


    crewStatus.textContent =
      data.crewai_used
        ? "Active"
        : "Fallback";


    n8nStatus.textContent =
      data.n8n_notified
        ? "Notified"
        : "Optional";


    renderPlan(
      data.plan
    );


    renderAgentResults(
      data.agent_results
    );


    renderReport(
      data.final_report
    );


    setStatus(
      "Completed",
      "completed"
    );


  } catch (
    error
  ) {

    console.error(
      error
    );


    setStatus(
      "Failed",
      "failed"
    );


    workflowId.textContent =
      "Failed";


    reportCard.classList.remove(
      "hidden"
    );


    executiveSummary.innerHTML =
      `
        <p>
          ${escapeHtml(
            error.message
          )}
        </p>
      `;


    keyFindings.innerHTML =
      `
        <p>
          Workflow execution did not complete.
        </p>
      `;


    actions.innerHTML =
      `
        <p>
          Check the VS Code terminal for the backend error.
        </p>
      `;


    recommendation.innerHTML =
      `
        <p>
          Correct the error and run the workflow again.
        </p>
      `;


    reportElement.textContent =
      error.message;

  } finally {

    runButton.disabled =
      false;


    runButton.innerHTML =
      `
        <span class="play-icon">
          ▷
        </span>

        Run multi-agent workflow

        <span>
          →
        </span>
      `;
  }
}


runButton.addEventListener(
  "click",
  runWorkflow
);


goalInput.addEventListener(
  "keydown",
  (
    event
  ) => {

    if (
      event.ctrlKey
      &&
      event.key === "Enter"
    ) {

      runWorkflow();
    }
  }
);