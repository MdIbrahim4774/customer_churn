import { useState } from "react";
import CustomerSearch from "./Pages/CustomerSearch";
import ChurnSummary from "./Pages/ChurnSummary";
import HighRiskCustomers from "./Pages/HighRiskCustomers";
import ChurnPrediction from "./Pages/ChurnPrediction";
import "./App.css";

function App() {
  const [page, setPage] = useState("summary");

  return (
    <div>
      <nav className="navbar">
        <button onClick={() => setPage("summary")}>
          Churn Summary
        </button>

        <button onClick={() => setPage("search")}>
          Customer Search
        </button>

        <button onClick={() => setPage("high-risk")}>
          High-Risk Customers
        </button>
        <button onClick={() => setPage("prediction")}>
        Churn Prediction
        </button>
      </nav>

      {page === "summary" && <ChurnSummary />}

      {page === "search" && <CustomerSearch />}

      {page === "high-risk" && <HighRiskCustomers />}

      {page === "prediction" && <ChurnPrediction />}
    </div>
  );
}

export default App;