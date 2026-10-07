import { useState } from "react";
import { api } from "../api";

function ChurnPrediction() {
  const [form, setForm] = useState({
    tenure: "",
    monthly_charges: "",
    contract_type: "Month-to-month",
    service_count: "",
    internet_service: "DSL"
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm({
      ...form,
      [name]: value
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await api.post("/predict-churn", {
        tenure: Number(form.tenure),
        monthly_charges: Number(form.monthly_charges),
        contract_type: form.contract_type,
        service_count: Number(form.service_count),
        internet_service: form.internet_service
      });

      setResult(response.data);
    } catch (error) {
      if (error.response?.status === 422) {
        const detail = error.response.data.detail;

        if (Array.isArray(detail)) {
          setError(
            detail
              .map(
                (item) =>
                  `${item.loc.join(".")}: ${item.msg}`
              )
              .join(", ")
          );
        } else {
          setError(String(detail));
        }
      } else if (error.response) {
        setError(
          error.response.data?.detail ||
          "Prediction request failed."
        );
      } else {
        setError("Unable to connect to the prediction API.");
      }
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevel = (score) => {
    if (score < 0.3) {
      return "low";
    }

    if (score <= 0.6) {
      return "medium";
    }

    return "high";
  };

  const riskLevel = result
    ? getRiskLevel(result.risk_score)
    : "";

  return (
    <div className="prediction-page">
      <h1>Churn Prediction</h1>

      <p>
        Enter customer information to estimate the likelihood
        of customer churn.
      </p>

      <form
        onSubmit={handleSubmit}
        className="prediction-form"
      >
        <div>
          <label>Tenure</label>

          <input
            type="number"
            name="tenure"
            value={form.tenure}
            onChange={handleChange}
            min="0"
            max="100"
            required
          />
        </div>

        <div>
          <label>Monthly Charges</label>

          <input
            type="number"
            name="monthly_charges"
            value={form.monthly_charges}
            onChange={handleChange}
            min="0.01"
            step="0.01"
            required
          />
        </div>

        <div>
          <label>Contract Type</label>

          <select
            name="contract_type"
            value={form.contract_type}
            onChange={handleChange}
          >
            <option value="Month-to-month">
              Month-to-month
            </option>

            <option value="One year">
              One year
            </option>

            <option value="Two year">
              Two year
            </option>
          </select>
        </div>

        <div>
          <label>Internet Service</label>

          <select
            name="internet_service"
            value={form.internet_service}
            onChange={handleChange}
          >
            <option value="DSL">
              DSL
            </option>

            <option value="Fiber optic">
              Fiber optic
            </option>

            <option value="No">
              No
            </option>
          </select>
        </div>

        <div>
          <label>Service Count</label>

          <input
            type="number"
            name="service_count"
            value={form.service_count}
            onChange={handleChange}
            min="0"
            max="6"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Predicting..."
            : "Predict Churn"}
        </button>
      </form>

      {error && (
        <div className="prediction-error">
          {error}
        </div>
      )}

      {result && (
        <div
          className={`prediction-result ${riskLevel}`}
        >
          <h2>Prediction Result</h2>

          <div className="risk-score">
            {(result.risk_score * 100).toFixed(1)}%
          </div>

          <p>
            <strong>Prediction:</strong>{" "}
            {result.prediction}
          </p>

          <p>
            <strong>Confidence:</strong>{" "}
            {(result.confidence * 100).toFixed(1)}%
          </p>

          <p>
            <strong>Risk Level:</strong>{" "}
            {riskLevel === "low"
              ? "Low Risk"
              : riskLevel === "medium"
              ? "Medium Risk"
              : "High Risk"}
          </p>
        </div>
      )}
    </div>
  );
}

export default ChurnPrediction;