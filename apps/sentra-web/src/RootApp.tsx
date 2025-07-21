// src/RootApp.tsx
// This file sets up the main application routing and authentication context
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { useAuth } from './context/useAuth';
import App from './App';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Spinner from './components/Spinner';
import { ToastContainer } from 'react-toastify';

function AppGuard() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div
        style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
      >
        <Spinner />
      </div>
    );
  }

  if (!user) {
    console.warn('User not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }

  return <App />;
}

export default function RootApp() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/*" element={<AppGuard />} />
        </Routes>
      </BrowserRouter>
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar
        newestOnTop
        closeOnClick
        pauseOnFocusLoss
        draggable
        pauseOnHover
        toastClassName="sentra-toast"
        className="sentra-toast-body"
      />
    </AuthProvider>
  );
}
