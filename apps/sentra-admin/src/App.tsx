import { BrowserRouter as Router } from 'react-router-dom';
import AppRoutes from './routes/AppRoutes';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import './App.css';

const App: React.FC = () => {
  return (
    <Router>
      <div className="dashboard-layout">
        <Sidebar />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <TopBar />
          <main className="page-content">
            <AppRoutes />
          </main>
        </div>
      </div>
    </Router>
  );
};

export default App;
