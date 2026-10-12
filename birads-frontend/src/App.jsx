import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "@/components/ProtectedRoute";
import Layout from "@/components/Layout";
import Login from "@/routes/Login";
import Home from "@/routes/Home";
import Worklist from "@/routes/Worklist";
import Study from "@/routes/Study";
import PatientHistory from "@/routes/PatientHistory";
import CaseView from "@/routes/CaseView";
import ChangePassword from "@/routes/ChangePassword";
import AdminUsers from "@/routes/AdminUsers";
import AdminDashboard from "@/routes/AdminDashboard";

export default function App() {
  return (
    <BrowserRouter
      future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
    >
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedRoute />}>
          <Route path="change-password" element={<ChangePassword />} />
          <Route element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="worklist" element={<Worklist />} />
            <Route path="study" element={<Study />} />
            <Route path="case/:id" element={<CaseView />} />
            <Route path="patient/:ref" element={<PatientHistory />} />
            <Route path="admin" element={<AdminDashboard />} />
            <Route path="admin/users" element={<AdminUsers />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
