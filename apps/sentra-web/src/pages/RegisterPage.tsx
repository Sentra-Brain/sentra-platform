import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { userService } from '../services/userService';
import { publicService } from '../services/publicService';


export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [slots, setSlots] = useState<number | null>(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    publicService.getSettings()
      .then(data => setSlots(data.available_slots))
      .catch(() => setSlots(null));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (!username || !fullName || !email || !password) {
      setError('All fields are required.');
      return;
    }

    try {
      const response = await userService.signup({ username, email, full_name: fullName, password });
      setMessage(response.message);
      setTimeout(() => navigate('/login'), 5000);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Registration failed.');
    }
  };

  return (
    <div className="login-page">
      <form className="card relative" onSubmit={handleSubmit}>
        <img
          src="/sentra_brain_logo_512.png"
          alt="Sentra Brain Logo"
          className="absolute -top-25 left-1/2 transform -translate-x-1/2 w-24 drop-shadow-lg"
          loading="lazy"
        />

        <h2 className="card-title">Register</h2>

        {slots !== null && (
          <div className="text-sm text-sentra-accent mb-2">
            {slots === -1 ? 'Unlimited slots available' : `Slots available: ${slots}`}
          </div>
        )}

        {error && <div className="text-red-500 text-sm mb-3">{error}</div>}
        {message && <div className="text-green-500 text-sm mb-3">{message}</div>}

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          className="card-input"
        />
        <input
          type="text"
          placeholder="Full Name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
          className="card-input"
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="card-input"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="card-input"
        />

        <button type="submit" className="card-button mb-4" disabled={slots === 0}>
          Register
        </button>

        <div className="text-center text-sm">
          Already have an account?{' '}
          <a href="/login" className="card-link font-medium">
            Login
          </a>
        </div>
      </form>
    </div>
  );
}
