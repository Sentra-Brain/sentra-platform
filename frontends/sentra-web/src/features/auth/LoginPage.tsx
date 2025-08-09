// src/features/auth/LoginPage.tsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppSelector } from '@store/hooks'
import { useAuth } from './useAuth'
import { useLocation } from 'react-router-dom'
import './LoginPage.css'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [remember, setRemember] = useState(false)
  const [error, setError] = useState('')

  const navigate = useNavigate()
  const { login } = useAuth()
  const token = useAppSelector((state) => state.auth.token)
  const rehydrated = useAppSelector((state) => state.auth.rehydrated)
  const location = useLocation()

  useEffect(() => {
    if (rehydrated && token && location.pathname === '/login') {
      navigate('/', { replace: true })
    }
  }, [rehydrated, token, navigate, location.pathname])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!email || !password) {
      setError('Email and password are required.')
      return
    }

    const success = await login(email, password, remember)
    if (!success) {
      setError('Invalid credentials.')
    }
  }


  return (
    <div className="login-page">
      <form className="card relative" onSubmit={handleSubmit}>
        <img
          src="/sentra_brain_logo_512.png"
          alt="Sentra Brain Logo"
          className="absolute -top-25 left-1/2 transform -translate-x-1/2 w-24 drop-shadow-lg"
          loading="lazy"
        />

        <h2 className="card-title">Login</h2>

        {error && <div className="text-red-500 text-sm mb-4">{error}</div>}

        <input
          id="email"
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="card-input"
        />

        <input
          id="password"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="card-input"
        />

        <div className="flex justify-between items-center text-sm mb-6 whitespace-nowrap">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
              className="accent-[var(--sentra-accent)]"
            />
            Remember me
          </label>
          <a href="#" className="card-link">
            Forgot password?
          </a>
        </div>

        <button type="submit" className="card-button mb-4">
          LOGIN
        </button>

        <div className="text-center text-sm">
          Don't have an account?{" "}
          <a href="/register" className="card-link font-medium">
            Sign up
          </a>
        </div>
      </form>
    </div>
  );
}
