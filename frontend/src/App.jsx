
import "./App.css";

const transactions = [
  {
    id: "TXN-10042",
    customer: "Customer A",
    amount: "$4,850.00",
    location: "Lagos, NG",
    risk: "High",
    status: "Under review",
  },
  {
    id: "TXN-10041",
    customer: "Customer B",
    amount: "$125.50",
    location: "Abuja, NG",
    risk: "Low",
    status: "Cleared",
  },
  {
    id: "TXN-10040",
    customer: "Customer C",
    amount: "$2,760.00",
    location: "London, UK",
    risk: "Medium",
    status: "Flagged",
  },
  {
    id: "TXN-10039",
    customer: "Customer D",
    amount: "$7,200.00",
    location: "Accra, GH",
    risk: "High",
    status: "Under review",
  },
];

const metrics = [
  { label: "Transactions analyzed", value: "12,840", note: "Demo value" },
  { label: "Flagged transactions", value: "284", note: "Demo value" },
  { label: "Open investigations", value: "37", note: "Demo value" },
  { label: "High-risk alerts", value: "18", note: "Demo value" },
];

function App() {
  return (
    <div className="app-shell">
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
          <a className="nav-item active" href="#overview">▦ Dashboard</a>
          <a className="nav-item" href="#transactions">⇄ Transactions</a>
          <a className="nav-item" href="#alerts">⚑ Fraud alerts</a>
          <a className="nav-item" href="#investigations">⌕ Investigations</a>
          <a className="nav-item" href="#reports">▤ Reports</a>
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

      <main className="main-content" id="overview">
        <header className="topbar">
          <div>
            <p className="eyebrow">FRAUD OPERATIONS / OVERVIEW</p>
            <h1>Fraud Detection Dashboard</h1>
            <p className="subtitle">
              Monitor transaction risk and investigate suspicious activity.
            </p>
          </div>
          <div className="topbar-right">
            <span className="environment">DEMO DATA</span>
            <div className="avatar">AD</div>
          </div>
        </header>

        <section className="metrics-grid">
          {metrics.map((metric) => (
            <article className="metric-card" key={metric.label}>
              <p>{metric.label}</p>
              <h2>{metric.value}</h2>
              <span>{metric.note}</span>
            </article>
          ))}
        </section>

        <section className="section-heading" id="alerts">
          <div>
            <h2>Recent transaction activity</h2>
            <p>Example records for the initial dashboard layout.</p>
          </div>
          <button className="secondary-button" onClick={() => window.location.reload()}>
            Refresh preview
          </button>
        </section>

        <section className="table-card" id="transactions">
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Transaction ID</th>
                  <th>Customer</th>
                  <th>Amount</th>
                  <th>Location</th>
                  <th>Risk level</th>
                  <th>Investigation status</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td className="transaction-id">{transaction.id}</td>
                    <td>{transaction.customer}</td>
                    <td className="amount">{transaction.amount}</td>
                    <td>{transaction.location}</td>
                    <td>
                      <span className={`risk-badge ${transaction.risk.toLowerCase()}`}>
                        {transaction.risk}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`status-badge ${transaction.status
                          .toLowerCase()
                          .replaceAll(" ", "-")}`}
                      >
                        {transaction.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <footer className="table-footer">
            <span>Showing 4 example transactions</span>
            <span>Not connected to live transaction data</span>
          </footer>
        </section>

        <section className="notice" id="investigations">
          <div className="notice-icon">i</div>
          <p>
            <strong>Investigation principle:</strong> A high-risk score is a
            signal for review, not proof of fraud. Decisions must be supported
            by evidence.
          </p>
        </section>

        <footer className="page-footer" id="reports">
          Fraud Detection and Investigation Platform
          <span>Initial frontend prototype</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
