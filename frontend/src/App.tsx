import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./pages/login";

function App() {
  return (
    <>
      <Routes>
        <Route index element={<Navigate to="/login" />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </>
  );
}

export default App;
