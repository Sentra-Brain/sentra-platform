import { Navigate, Outlet } from 'react-router-dom'
import { useSelector } from 'react-redux'
import type { RootState } from '../store'
import Layout from '../components/layout/Layout'

export default function PrivateRoute() {
  const isAuthenticated = useSelector((state: RootState) => !!state.auth.token)

  return isAuthenticated ? (
    <Layout>
      <Outlet />
    </Layout>
  ) : (
    <Navigate to="/login" replace />
  )
}
