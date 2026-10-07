import { useState } from "react";
import { api } from "../api";

function CustomerSearch() {
  const [customerId, setCustomerId] = useState("");
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const searchCustomer = async () => {
    if (!customerId.trim()) {
      setError("Please enter a customer ID.");
      return;
    }

    setLoading(true);
    setError("");
    setCustomer(null);

    try {
      const response = await api.get(
        `/customer/${customerId.trim()}`
      );

      setCustomer(response.data);
    } catch (error) {
      if (error.response?.status === 404) {
        setError("Customer not found");
      } else {
        setError("Unable to fetch customer details.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="customer-search">
      <h2>Customer Search</h2>

      <div>
        <input
          type="text"
          value={customerId}
          onChange={(event) => setCustomerId(event.target.value)}
          placeholder="Enter customer ID"
        />

        <button onClick={searchCustomer}>
          Search
        </button>
      </div>

      {loading && <p>Loading...</p>}

      {error && <p>{error}</p>}

      {customer && (
        <div className="customer-card">
          <h3>Customer Details</h3>

          <p>
            <strong>Customer ID:</strong>{" "}
            {customer.customer_id}
          </p>

          <p>
            <strong>Tenure:</strong>{" "}
            {customer.tenure}
          </p>

          <p>
            <strong>Contract:</strong>{" "}
            {customer.contract_type}
          </p>

          <p>
            <strong>Internet Service:</strong>{" "}
            {customer.internet_service}
          </p>

          <p>
            <strong>Monthly Charges:</strong>{" "}
            ${customer.monthly_charges}
          </p>

          <p>
            <strong>Churn Status:</strong>{" "}
            <span
              className={
                customer.churn === 1
                  ? "churned"
                  : "active"
              }
            >
              {customer.churn === 1
                ? "Churned"
                : "Active"}
            </span>
          </p>
        </div>
      )}
    </div>
  );
}

export default CustomerSearch;