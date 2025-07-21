// src/App.tsx
import AppRoutes from './routes/AppRoutes';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';

const App: React.FC = () => {
  return (
    <div style={{ display: "flex", height: "100vh", width: "100vw" }}>
      <Sidebar />
        <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        <TopBar />
        <main className="main-content">
          <AppRoutes />
        </main>
      </div>
    </div>
  );
};

export default App;
