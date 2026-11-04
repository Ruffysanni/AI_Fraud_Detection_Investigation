
import { useCallback, useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";


const metricDefinitions = [
  {
    label: "Transactions analyzed",
    key: "transactions_analyzed",
  },
  {
    label: "Flagged transactions",
    key: "flagged_transactions",
  },
  {
    label: "Open investigations",
    key: "open_investigations",
  },
  {
    label: "High-risk alerts",
    key: "high_risk_alerts",
  },
];


function App() {
  const [formData, setFormData] = useState({
    step: "100",
    type: "TRANSFER",
    amount: "5000",
    oldbalanceOrg: "10000",
    newbalanceOrig: "5000",
    oldbalanceDest: "2000",
    newbalanceDest: "7000",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [transactions, setTransactions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [dashboardMetrics, setDashboardMetrics] = useState(null);

  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState("");
  const [refreshSuccess, setRefreshSuccess] = useState("");

  // Load transaction history and investigation alerts
  
// Load transaction history, investigation alerts and dashboard metrics
const loadDashboardData = useCallback(async () => {
  setHistoryLoading(true);
  setHistoryError("");
  setRefreshSuccess("");

  try {
    const [
      transactionsResponse,
      alertsResponse,
      metricsResponse,
    ] = await Promise.all([
      fetch(`${API_BASE_URL}/transactions`),
      fetch(`${API_BASE_URL}/alerts`),
      fetch(`${API_BASE_URL}/dashboard/metrics`),
    ]);

    if (
      !transactionsResponse.ok ||
      !alertsResponse.ok ||
      !metricsResponse.ok
    ) {
      throw new Error(
        "The API could not load dashboard information."
      );
    }

    const [
      transactionsData,
      alertsData,
      metricsData,
    ] = await Promise.all([
      transactionsResponse.json(),
      alertsResponse.json(),
      metricsResponse.json(),
    ]);

    if (
      !Array.isArray(transactionsData) ||
      !Array.isArray(alertsData) ||
      !metricsData ||
      typeof metricsData !== "object"
    ) {
      throw new Error(
        "Unexpected data format returned by the API."
      );
    }

    setTransactions(transactionsData);
    setAlerts(alertsData);
    setDashboardMetrics(metricsData);
    setRefreshSuccess("Dashboard data refreshed successfully.");

  } catch (err) {
    setHistoryError(
      err.message || "Unable to load dashboard information."
    );
  } finally {
    setHistoryLoading(false);
  }
}, []);


  // Load dashboard data when the component mounts
  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Handle form input changes
  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  // Submit transaction for fraud assessment
  async function handleSubmit(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    const payload = {
      ...formData,
      step: Number(formData.step),
      amount: Number(formData.amount),
      oldbalanceOrg: Number(formData.oldbalanceOrg),
      newbalanceOrig: Number(formData.newbalanceOrig),
      oldbalanceDest: Number(formData.oldbalanceDest),
      newbalanceDest: Number(formData.newbalanceDest),
    };

    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join(", ")
          : data.detail;

        throw new Error(detail || "Prediction request failed.");
      }

      setResult(data);

      // Refresh dashboard after successful assessment
      await loadDashboardData();
    } catch (err) {
      setError(
        err.message ||
          "Could not reach the API. Check that FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">F</div>

          <div>
            <h2>Fraud Monitor</h2>
            <span>Investigation Platform</span>
          </div>
        </div>

        <p className="nav-label">WORKSPACE</p>

        <nav>
          <a className="nav-item active" href="#overview">
            ▦ Dashboard
          </a>

          <a className="nav-item" href="#transactions">
            ⇄ Transactions
          </a>

          <a className="nav-item" href="#alerts">
            ⚑ Fraud alerts
          </a>

          <a className="nav-item" href="#investigations">
            ⌕ Investigations
          </a>

          <a className="nav-item" href="#reports">
            ▤ Reports
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="status-dot" />

            <div>
              <strong>System workspace</strong>
              <p>Frontend preview</p>
            </div>
          </div>

          <div className="profile">
            <div className="avatar">AD</div>

            <div>
              <strong>Analyst Dashboard</strong>
              <p>Investigation team</p>
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-content" id="overview">

        {/* HEADER */}
        <header className="topbar">
          <div>
            <p className="eyebrow">FRAUD OPERATIONS / OVERVIEW</p>

            <h1>Fraud Detection Dashboard</h1>

            <p className="subtitle">
              Monitor transaction risk and investigate suspicious activity.
            </p>
          </div>

          <div className="topbar-right">
            <span className="environment">LIVE DATABASE DATA</span>
            <div className="avatar">AD</div>
          </div>
        </header>

        {/* DASHBOARD METRICS */}
        
{/* DASHBOARD METRICS */}
<section className="metrics-grid">
  {metricDefinitions.map((metric) => (
    <article className="metric-card" key={metric.key}>
      <p>{metric.label}</p>

      <h2>
        {dashboardMetrics
          ? Number(dashboardMetrics[metric.key]).toLocaleString()
          : "—"}
      </h2>

      <span>
        {dashboardMetrics
          ? "Live database value"
          : historyLoading
            ? "Loading..."
            : "Unavailable"}
      </span>
    </article>
  ))}
</section>


        {/* TRANSACTION ASSESSMENT */}
        <section className="assessment-section" id="assessment">
          <div className="section-heading">
            <div>
              <h2>Assess a transaction</h2>

              <p>
                Submit transaction details to the machine-learning model for a
                risk estimate.
              </p>
            </div>

            <span className="environment">MODEL PREDICTION</span>
          </div>

          <form className="assessment-card" onSubmit={handleSubmit}>
            <div className="form-grid">

              <label>
                Transaction time step
                <input
                  name="step"
                  type="number"
                  min="0"
                  value={formData.step}
                  onChange={handleChange}
                  required
                />
              </label>

              <label>
                Transaction type
                <select
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                >
                  {[
                    "CASH_IN",
                    "CASH_OUT",
                    "DEBIT",
                    "PAYMENT",
                    "TRANSFER",
                  ].map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Transaction amount
                <input
                  name="amount"
                  type="number"
                  min="0"
                  step="any"
                  value={formData.amount}
                  onChange={handleChange}
                  required
                />
              </label>

              <label>
                Origin balance before
                <input
                  name="oldbalanceOrg"
                  type="number"
                  min="0"
                  step="any"
                  value={formData.oldbalanceOrg}
                  onChange={handleChange}
                  required
                />
              </label>

              <label>
                Origin balance after
                <input
                  name="newbalanceOrig"
                  type="number"
                  min="0"
                  step="any"
                  value={formData.newbalanceOrig}
                  onChange={handleChange}
                  required
                />
              </label>

              <label>
                Destination balance before
                <input
                  name="oldbalanceDest"
                  type="number"
                  min="0"
                  step="any"
                  value={formData.oldbalanceDest}
                  onChange={handleChange}
                  required
                />
              </label>

              <label>
                Destination balance after
                <input
                  name="newbalanceDest"
                  type="number"
                  min="0"
                  step="any"
                  value={formData.newbalanceDest}
                  onChange={handleChange}
                  required
                />
              </label>

            </div>

            <button
              className="primary-button"
              type="submit"
              disabled={loading}
            >
              {loading ? "Assessing transaction..." : "Assess transaction"}
            </button>

            {error && (
              <p className="assessment-error" role="alert">
                {error}
              </p>
            )}

            {/* ASSESSMENT RESULT */}
            {result && (
              <div className="assessment-result" aria-live="polite">
                <p className="eyebrow">MODEL ASSESSMENT RESULT</p>

                <div className="result-grid">
                  <div>
                    <span>Fraud score</span>

                    <h3>
                      {(Number(result.fraud_score) * 100).toFixed(2)}%
                    </h3>
                  </div>

                  <div>
                    <span>Risk level</span>

                    <h3 className={`risk-badge ${result.risk_level}`}>
                      {result.risk_level.toUpperCase()}
                    </h3>
                  </div>

                  <div>
                    <span>Prediction</span>

                    <h3>
                      {result.prediction_label === "fraud_suspected"
                        ? "Fraud suspected"
                        : "Legitimate predicted"}
                    </h3>
                  </div>
                </div>

                <p className="result-disclaimer">
                  {result.disclaimer}
                </p>
              </div>
            )}
          </form>
        </section>

        {/* TRANSACTION HISTORY HEADING */}
        <section className="section-heading">
          <div>
            <h2>Recent transaction activity</h2>

            <p>
              Assessed transactions retrieved from the database.
            </p>
          </div>

          <button
            className="secondary-button"
            type="button"
            onClick={loadDashboardData}
            disabled={historyLoading}
          >
            {historyLoading ? "Refreshing..." : "Refresh data"}
          </button>
        </section>
        {refreshSuccess && !historyLoading && (
  <p className="refresh-success" role="status">
    {refreshSuccess}
  </p>
)}

        {/* TRANSACTION HISTORY TABLE */}
        <section className="table-card" id="transactions">
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Transaction ID</th>
                  <th>Step</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th>Fraud score</th>
                  <th>Risk level</th>
                  <th>Assessed at</th>
                </tr>
              </thead>

              <tbody>
  {historyLoading && (
    <tr>
      <td colSpan={7} className="table-message">
        Loading transaction records...
      </td>
    </tr>
  )}

  {!historyLoading &&
    transactions.map((transaction) => (
      <tr key={transaction.transaction_id}>
        <td className="transaction-id">
          {transaction.transaction_id}
        </td>

        <td>{transaction.step}</td>
        <td>{transaction.type}</td>

        <td className="amount">
          {Number(transaction.amount).toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}
        </td>

        <td>
          {(Number(transaction.fraud_score) * 100).toFixed(2)}%
        </td>

        <td>
          <span className={`risk-badge ${transaction.risk_level}`}>
            {transaction.risk_level.toUpperCase()}
          </span>
        </td>

        <td>
          {new Date(transaction.created_at).toLocaleString()}
        </td>
      </tr>
    ))}

  {!historyLoading &&
    !historyError &&
    transactions.length === 0 && (
      <tr>
        <td colSpan={7} className="table-message">
          No assessed transactions found.
        </td>
      </tr>
    )}
</tbody>
            </table>
          </div>

          <footer className="table-footer">
            <span>
              {historyLoading
                ? "Loading transactions..."
                : `Showing ${transactions.length} saved transactions`}
            </span>

            <span>Source: PostgreSQL via FastAPI</span>
          </footer>
        </section>

        {/* INVESTIGATION ALERTS HEADING */}
        <section className="section-heading" id="alerts">
          <div>
            <h2>Investigation alerts</h2>

            <p>
              Transactions requiring further review.
            </p>
          </div>
        </section>

        {/* INVESTIGATION ALERTS TABLE */}
        <section className="table-card" id="investigation-alerts">
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Alert ID</th>
                  <th>Transaction ID</th>
                  <th>Severity</th>
                  <th>Reason</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Created at</th>
                </tr>
              </thead>

              <tbody>
  {historyLoading && (
    <tr>
      <td colSpan={7} className="table-message">
        Loading investigation alerts...
      </td>
    </tr>
  )}

  {!historyLoading &&
    alerts.map((alert) => (
      <tr key={alert.alert_id}>
        <td>{alert.alert_id}</td>
        <td>{alert.transaction_id}</td>

        <td>
          <span className={`risk-badge ${alert.severity}`}>
            {alert.severity.toUpperCase()}
          </span>
        </td>

        <td>{alert.reason}</td>

        <td className="amount">
          {Number(alert.amount).toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}
        </td>

        <td>
          <span className={`status-badge ${alert.status}`}>
            {alert.status.toUpperCase()}
          </span>
        </td>

        <td>
          {new Date(alert.created_at).toLocaleString()}
        </td>
      </tr>
    ))}

  {!historyLoading &&
    !historyError &&
    alerts.length === 0 && (
      <tr>
        <td colSpan={7} className="table-message">
          No investigation alerts found.
        </td>
      </tr>
    )}
</tbody>
            </table>
          </div>

          <footer className="table-footer">
            <span>
              {historyLoading
                ? "Loading alerts..."
                : `${alerts.length} alerts retrieved`}
            </span>

            <span>Source: PostgreSQL via FastAPI</span>
          </footer>
        </section>

        {/* DASHBOARD ERROR MESSAGE */}
{historyError && (
  <div className="dashboard-error" role="alert">
    <strong>Dashboard data unavailable</strong>
    <p>{historyError}</p>

    <button
      className="secondary-button"
      type="button"
      onClick={loadDashboardData}
      disabled={historyLoading}
    >
      {historyLoading ? "Retrying..." : "Try again"}
    </button>
  </div>
)}

        {/* INVESTIGATION NOTICE */}
        <section className="notice" id="investigations">
          <div className="notice-icon">i</div>

          <p>
            <strong>Investigation principle:</strong> A high-risk score is a
            signal for review, not proof of fraud. Decisions must be supported
            by evidence.
          </p>
        </section>

        {/* PAGE FOOTER */}
        <footer className="page-footer" id="reports">
          Fraud Detection and Investigation Platform

          <span>Initial frontend prototype</span>
        </footer>

      </main>
    </div>
  );
}

export default App;
