import React from "react";
import { useNavigate } from "react-router-dom";

const Cancel = () => {
  const navigate = useNavigate();
  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <h1>❌ Payment Cancelled</h1>
      <p>You cancelled the payment process. Try again when you're ready.</p>
      <button
        onClick={() => navigate("/")}
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          fontSize: "16px",
          cursor: "pointer",
        }}
      >
        Go to Home
      </button>
    </div>
  );
};

export default Cancel;