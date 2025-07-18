import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';
import './LoginPage.css';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!email || !password) {
      setError('Email and password are required.');
      return;
    }
    const success = await login(email, password, remember);
    if (success) {
      navigate('/chat');
    } else {
      setError('Invalid credentials.');
    }
  };

  return (
    <div className="login-page">
      <form
        className="login-card relative  bg-[var(--sentra-primary-dark)] text-[var(--sentra-text)] p-8 rounded-2xl border-2 border-[var(--sentra-accent-light)] hover:border-[var(--sentra-accent)] transition-all duration-300 shadow-sentra w-full max-w-md"
        onSubmit={handleSubmit}
      >
        <img
          src="/sentra_brain_logo_512.png"
          alt="Sentra Brain Logo"
          className="absolute -top-25 left-1/2 transform -translate-x-1/2 w-24 drop-shadow-lg"
          loading="lazy"
        />

        <h2 className="text-xl font-bold mb-4 text-center">Login</h2>

        {error && <div className="text-red-500 text-sm mb-4">{error}</div>}

        <input
          id="email"
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full p-2 rounded-md bg-black/30 border border-[var(--sentra-accent-light)] text-white mb-4 focus:outline-none focus:ring-2 focus:ring-[var(--sentra-accent)]"
        />

        <input
          id="password"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full p-2 rounded-md bg-black/30 border border-[var(--sentra-accent-light)] text-white mb-4 focus:outline-none focus:ring-2 focus:ring-[var(--sentra-accent)]"
        />

        <div className="flex justify-between items-center text-sm mb-6 whitespace-nowrap">
          <label className="flex items-center gap-2 ">
            <input
              type="checkbox"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
              className="accent-[var(--sentra-accent)] mt-0.5"
            />
            Remember me
          </label>
          <a
            href="#"
            className="text-[var(--sentra-accent-light)] hover:text-[var(--sentra-accent)] transition"
          >
            Forgot password?
          </a>
        </div>

        <button
          type="submit"
          className="w-full py-2 bg-[var(--sentra-accent)] text-[var(--sentra-primary)] font-semibold rounded-lg hover:bg-[var(--sentra-accent-light)] transition mb-4"
        >
          LOGIN
        </button>

        <div className="text-center text-sm">
          Don't have an account?{' '}
          <a
            href="#"
            className="text-[var(--sentra-accent-light)] hover:text-[var(--sentra-accent)] font-medium transition"
          >
            Sign up
          </a>
        </div>
      </form>
    </div>
  );
}
