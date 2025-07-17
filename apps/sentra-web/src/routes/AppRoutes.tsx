import { Routes, Route, Navigate } from 'react-router-dom';
import Chat from '../pages/Chat';
import Users from '../pages/Users';
import Settings from '../pages/Settings';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import PrivateRoute from './PrivateRoute';

const AppRoutes: React.FC = () => (
  <Routes>
    <Route path="/" element={<Navigate to="/chat" replace />} />
    <Route path="/chat" element={
      <PrivateRoute>
        <Chat />
      </PrivateRoute>
    } />
    <Route path="/users" element={
      <PrivateRoute>
        <Users />
      </PrivateRoute>
    } />
    <Route path="/settings" element={
      <PrivateRoute>
        <Settings />
      </PrivateRoute>
    } />
    <Route path="/login" element={<LoginPage />} />
    <Route path="/register" element={<RegisterPage />} />
  </Routes>
);

export default AppRoutes;
