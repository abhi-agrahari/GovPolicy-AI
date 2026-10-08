import { authApi } from "../api";
import "./Login.css";

function Login() {
  return (
    <div className="login-page">
      <div className="login-card">
        <h1>GovPolicy AI</h1>

        <p className="login-subtitle">
          Understand government policies with AI
        </p>

        <button className="google-login-btn" onClick={authApi.login}>
          Continue with Google
        </button>
      </div>
    </div>
  );
}

export default Login;