import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import TaskWorkspace from "./pages/TaskWorkspace";
import { useAuth } from "./auth/AuthContext";

export default function App() {
  const { token } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={token ? <Navigate to="/" /> : <Login />}
      />
      <Route
        path="/register"
        element={token ? <Navigate to="/" /> : <Register />}
      />
      <Route
        path="/"
        element={token ? <Dashboard /> : <Navigate to="/login" />}
      />
      <Route
        path="/tasks/:id"
        element={token ? <TaskWorkspace /> : <Navigate to="/login" />}
      />
    </Routes>
  );
}
