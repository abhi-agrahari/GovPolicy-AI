import { useEffect, useState } from "react";
import { authApi } from "../api";
import "./Home.css";

function Home() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    authApi
      .getCurrentUser()
      .then((data) => {
        setUser(data);
      })
      .catch((error) => {
        console.error(error);
      });
  }, []);

  const handleLogout = async () => {
    await authApi.logout();

    window.location.reload();
  };

  return (
    <div className="home-page">
      <header className="navbar">
        <h2>GovPolicy AI</h2>

        <div className="user-section">
          {user?.authenticated && (
            <>
              <span>{user.email}</span>

              <button onClick={handleLogout}>
                Logout
              </button>
            </>
          )}
        </div>
      </header>

      <main className="home-content">
        <h1>Welcome to GovPolicy AI</h1>

        <p>
          Your AI assistant for understanding government policies.
        </p>
      </main>
    </div>
  );
}

export default Home;