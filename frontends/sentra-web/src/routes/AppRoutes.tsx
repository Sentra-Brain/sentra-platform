import { Routes, Route, Navigate } from "react-router-dom";
import PrivateRoute from "./PrivateRoute";

import LoginPage from "../features/auth/LoginPage";
import ChatPage from "../features/chat/ChatPage";

import SettingsPage from "../features/settings/SettingsPage";
import SearchPage from "../features/search/SearchPage";
import KnowledgePage from "@features/knowledge/KnowledgePage";

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />

      {/* Private */}
      <Route element={<PrivateRoute />}>
        {/* ✅ Main entry route */}
        <Route path="/c" element={<ChatPage />} />
        <Route path="/" element={<ChatPage />} />
        <Route path="/c/:id" element={<ChatPage />} />

        {/* Knowledge routes */}
        <Route path="/k" element={<Navigate to="/k/private" />} />
        <Route path="/k/:visibility" element={<KnowledgePage />} />

        <Route path="/s" element={<SettingsPage />} />
        <Route path="/search" element={<SearchPage />} />
      </Route>

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}
