import { useEffect, useState } from "react";
import { api } from "../api";

function HighRiskCustomers() {
  const [customers, setCustomers] = useState([]);
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sortAscending, setSortAscending] = useState(true);

  const fetchHighRiskCustomers = async (currentLimit) => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/customers/high-risk", {
        params: {
          limit: currentLimit
        }
      });

      setCustomers(response.data);
    } catch (error) {
      console.error("High-risk customer error:", error);
      setError("Failed to load high-risk customers.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHighRiskCustomers(limit);
  }, [limit]);

  const sortedCustomers = [...customers].sort((a, b) => {
    if (sortAscending) {
      return a.tenure - b.tenure;
    }

    return b.tenure - a.tenure;
  });

  const handleSort = () => {
    setSortAscending(!sortAscending);
  };

  const handleLoadMore = () => {
    setLimit(limit + 50);
  };

  if (loading) {
    return <h2>Loading high-risk customers...</h2>;
  }

  if (error) {
    return <h2>{error}</h2>;
  }

  return (
    <div className="high-risk-page">
      <h1>High-Risk Customers</h1>

      <p>
        Customers matching the defined business rules for high churn risk.
      </p>

      <div className="risk-count">
        {customers.length} high-risk customers identified
      </div>

      {customers.length === 0 ? (
        <p>No high-risk customers found</p>
      ) : (
        <>
          <table>
            <thead>
              <tr>
                <th>Customer ID</th>

                <th onClick={handleSort} className="sortable">
                  Tenure {sortAscending ? "↑" : "↓"}
                </th>

                <th>Monthly Charges</th>
                <th>Contract Type</th>
                <th>Risk Reason</th>
              </tr>
            </thead>

            <tbody>
              {sortedCustomers.map((customer) => (
                <tr key={customer.customer_id}>
                  <td>{customer.customer_id}</td>

                  <td>{customer.tenure}</td>

                  <td>
                    ${Number(customer.monthly_charges).toFixed(2)}
                  </td>

                  <td>{customer.contract_type}</td>

                  <td>{customer.risk_reason}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <button onClick={handleLoadMore}>
            Load More
          </button>
        </>
      )}
    </div>
  );
}

export default HighRiskCustomers;