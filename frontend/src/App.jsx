import { useState } from "react";
import Login from "./components/Login";
import SearchPage from "./components/SearchPage";
import "./index.css";

function App() {
  const [session, setSession] = useState(null);

  const handleLogin = (data) => {
    setSession(data);
  };

  const handleLogout = () => {
    setSession(null);
  };

  if (!session) {
    return <Login onLogin={handleLogin} />;
  }

  return <SearchPage session={session} onLogout={handleLogout} />;
}

export default App;
