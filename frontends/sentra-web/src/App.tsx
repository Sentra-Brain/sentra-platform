import { BrowserRouter } from 'react-router-dom'
import AppRoutes from './routes/AppRoutes'
import { Provider } from 'react-redux'
import { store } from './store'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import './styles/global.css'
import SessionInitializer from '@features/auth/SessionInitializer'
import ThemeProvider from '@layout/ThemeProvider'

export default function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <SessionInitializer />
        <ThemeProvider />
        <AppRoutes />
        <ToastContainer position="top-right" autoClose={3000} hideProgressBar />
      </BrowserRouter>
    </Provider>
  )
}
