import { useEffect, useState } from "react";

import Login from "./components/Login";
import Home from "./components/Home";
import { authApi } from "./api";

function App() {
  const [authenticated, setAuthenticated] = useState(null);

  useEffect(() => {
    authApi.getCurrentUser()
      .then((data) => {
        setAuthenticated(data.authenticated);
      })
      .catch(() => {
        setAuthenticated(false);
      });
  }, []);

  if (authenticated === null) {
    return <p>Loading...</p>;
  }

  return authenticated ? <Home /> : <Login />;
}

export default App;