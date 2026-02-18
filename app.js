const engineStatus = document.getElementById("engineStatus");
const calcButton = document.getElementById("calcButton");
const copyButton = document.getElementById("copyButton");
const errorBox = document.getElementById("errorBox");
const resultsEl = document.getElementById("results");
const scoreRangeEl = document.getElementById("scoreRange");
const factorListEl = document.getElementById("factorList");
const tipsListEl = document.getElementById("tipsList");

const form = document.getElementById("calcForm");

let pyodideReady = false;
let pyodide;
let calculateFn;
let latestCopyText = "";

function setError(message = "") {
  errorBox.textContent = message;
}

function num(id) {
  return Number(document.getElementById(id).value);
}

function validateInputs(inputs) {
  if (inputs.current_score < 300 || inputs.current_score > 850) {
    return "Current score must be between 300 and 850.";
  }
  if (inputs.utilization_percent < 0 || inputs.utilization_percent > 100) {
    return "Utilization must be between 0 and 100%.";
  }
  if (inputs.on_time_payments_percent < 0 || inputs.on_time_payments_percent > 100) {
    return "On-time payments must be between 0 and 100%.";
  }
  if (inputs.age_oldest_account_years < 0) {
    return "Age of oldest account cannot be negative.";
  }
  if (inputs.hard_inquiries_last_12mo < 0 || inputs.new_accounts_last_12mo < 0) {
    return "Inquiry and new account counts cannot be negative.";
  }
  return "";
}

async function initPyodide() {
  try {
    pyodide = await loadPyodide({
      indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/"
    });

    const modelCode = await fetch("model.py").then((r) => r.text());
    await pyodide.runPythonAsync(modelCode);
    calculateFn = pyodide.globals.get("calculate");

    pyodideReady = true;
    calcButton.disabled = false;
    engineStatus.innerHTML = "<span>Python engine loaded.</span>";
  } catch (err) {
    setError(`Failed to load calculator engine: ${err.message}`);
    engineStatus.innerHTML = "<span>Engine failed to load.</span>";
  }
}

function renderResult(result) {
  const range = result.estimated_new_score_range;
  scoreRangeEl.textContent = `Estimated score range: ${range.low} - ${range.high} (mid: ${range.mid})`;

  factorListEl.innerHTML = "";
  result.factor_breakdown.forEach((factor) => {
    const li = document.createElement("li");
    const sign = factor.impact >= 0 ? "+" : "";
    li.textContent = `${factor.factor}: ${sign}${factor.impact} (${factor.effect})`;
    factorListEl.appendChild(li);
  });

  tipsListEl.innerHTML = "";
  result.tips.forEach((tip) => {
    const li = document.createElement("li");
    li.textContent = tip;
    tipsListEl.appendChild(li);
  });

  latestCopyText = [
    `Credit Score Simulator`,
    `Range: ${range.low}-${range.high} (mid ${range.mid})`,
    "Factors:",
    ...result.factor_breakdown.map((f) => `- ${f.factor}: ${f.impact >= 0 ? "+" : ""}${f.impact}`),
    "Tips:",
    ...result.tips.map((t) => `- ${t}`),
    "Estimates only. Not financial advice."
  ].join("\n");

  copyButton.disabled = false;
  resultsEl.hidden = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setError("");

  if (!pyodideReady) {
    setError("Calculator engine is still loading. Please wait.");
    return;
  }

  const inputs = {
    current_score: num("current_score"),
    utilization_percent: num("utilization_percent"),
    on_time_payments_percent: num("on_time_payments_percent"),
    age_oldest_account_years: num("age_oldest_account_years"),
    hard_inquiries_last_12mo: num("hard_inquiries_last_12mo"),
    new_accounts_last_12mo: num("new_accounts_last_12mo"),
    derogatory_marks: num("derogatory_marks")
  };

  const validationError = validateInputs(inputs);
  if (validationError) {
    setError(validationError);
    return;
  }

  let pyInputs;
  let pyResult;

  try {
    pyInputs = pyodide.toPy(inputs);
    pyResult = calculateFn(pyInputs);
    const result = pyResult.toJs({ dict_converter: Object.fromEntries });
    renderResult(result);
  } catch (err) {
    setError(`Calculation failed: ${err.message}`);
  } finally {
    if (pyInputs) pyInputs.destroy();
    if (pyResult) pyResult.destroy();
  }
});

copyButton.addEventListener("click", async () => {
  if (!latestCopyText) return;
  try {
    await navigator.clipboard.writeText(latestCopyText);
    copyButton.textContent = "Copied";
    setTimeout(() => {
      copyButton.textContent = "Copy Results";
    }, 1100);
  } catch {
    setError("Unable to copy automatically. You can select and copy manually.");
  }
});

initPyodide();
