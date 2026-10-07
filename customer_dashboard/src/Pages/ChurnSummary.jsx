import { useEffect, useState } from "react";
import { api } from "../api";

function ChurnSummary() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchChurnSummary = async () => {
      try {
        const response = await api.get("/churn/summary");
        setData(response.data);
      } catch (error) {
        console.error("Churn summary error:", error);
        setError("Failed to load churn summary.");
      } finally {
        setLoading(false);
      }
    };

    fetchChurnSummary();
  }, []);

  if (loading) {
    return <h2>Loading churn summary...</h2>;
  }

  if (error) {
    return <h2>{error}</h2>;
  }

  return (
    <div className="churn-summary">
      <h1>Churn Summary</h1>

      <p>
        This page provides an overview of customer churn and
        compares churn rates across different contract types.
      </p>

      <div className="metric-container">
        <div className="metric-card">
          <h3>Total Customers</h3>
          <p>{data.total_customers}</p>
        </div>

        <div className="metric-card">
          <h3>Total Churned</h3>
          <p>{data.total_churned}</p>
        </div>

        <div className="metric-card">
          <h3>Churn Rate</h3>
          <p>{(data.churn_rate * 100).toFixed(1)}%</p>
        </div>
      </div>

      <h2>Churn Rate by Contract Type</h2>

      <table>
        <thead>
          <tr>
            <th>Contract Type</th>
            <th>Churn Rate</th>
            <th>Risk Level</th>
          </tr>
        </thead>

        <tbody>
          {data.by_contract.map((contract) => (
            <tr key={contract.contract_type}>
              <td>{contract.contract_type}</td>

              <td>
                {(contract.churn_rate * 100).toFixed(1)}%
              </td>

              <td>
                <div className="bar-container">
                  <div
                    className="churn-bar"
                    style={{
                      width: `${contract.churn_rate * 100}%`
                    }}
                  />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ChurnSummary;