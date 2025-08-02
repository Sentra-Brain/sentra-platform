import { BrowserRouter } from 'react-router-dom'
import AppRoutes from './routes/AppRoutes'
import { Provider } from 'react-redux'
import { store } from './store'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import './styles/global.css'
import SessionInitializer from './features/auth/SessionInitializer'
import ConversationsInitializer from './features/conversations/ConversationsInitializer'

export default function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <SessionInitializer />
        <ConversationsInitializer />
        <AppRoutes />
        <ToastContainer position="top-right" autoClose={3000} hideProgressBar />
      </BrowserRouter>
    </Provider>
  )
}
