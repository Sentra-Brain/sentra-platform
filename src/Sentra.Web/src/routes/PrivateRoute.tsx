import { Navigate, Outlet } from 'react-router-dom'
import { useSelector } from 'react-redux'
import type { RootState } from '../store'
import Layout from '../layout/Layout'
import ConversationsInitializer from '@features/conversations/ConversationsInitializer'

export default function PrivateRoute() {
  const isAuthenticated = useSelector((state: RootState) => !!state.auth.token)
  const isRehydrated = useSelector((state: RootState) => state.auth.rehydrated)

  if (!isRehydrated) {
    return null // or <LoadingScreen />
  }

  return isAuthenticated ? (
    <Layout>
      <ConversationsInitializer />
      <Outlet />
    </Layout>
  ) : (
    <Navigate to="/login" replace />
  )
}
