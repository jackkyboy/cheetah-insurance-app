import React, { useState } from "react";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleRequestReset = async () => {
    const response = await fetch("http://127.0.0.1:5000/api/admin/request-password-reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();
    setMessage(data.message || data.error);
  };

  return (
    <div>
      <h2>Forgot Password</h2>
      <input type="email" placeholder="Enter your email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <button onClick={handleRequestReset}>Send Reset Link</button>
      <p>{message}</p>
    </div>
  );
};

export default ForgotPassword;
