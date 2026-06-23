import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./pages/login";
import RegisterPage from "./pages/register";
import AppLayout from "./components/layouts/app-layout";
import DashboardPage from "./pages/dashboard";
import RoomsPage from "./pages/rooms";

function App() {
  return (
    <>
      <Routes>
        <Route index element={<Navigate to="/login" />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/rooms" element={<RoomsPage />} />
        </Route>
      </Routes>
    </>
  );
}

export default App;
