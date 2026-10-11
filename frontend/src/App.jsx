import { useEffect, useState } from "react";
import { ToastContainer, toast } from 'react-toastify';
import "react-toastify/dist/ReactToastify.css";

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

  return(
    <>
      {authenticated ? <Home /> : <Login />}
      
      <ToastContainer position="top-right" autoClose={3000} />
    </>
  )

}

export default App;