import './App.css'
import DashboardRoadmap from './components/DashboardRoadmap'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-content">
          <h1>🎬 Video Genius</h1>
          <p>AI-powered video generation platform</p>
        </div>
      </header>

      <nav className="app-nav">
        <div className="nav-container">
          <a href="/" className="nav-logo">
            📊 Dashboard
          </a>
          <ul className="nav-menu">
            <li><a href="/">Home</a></li>
            <li><a href="/dashboard">Dashboard</a></li>
            <li><a href={`${API_URL}/docs`} target="_blank" rel="noopener noreferrer">API Docs</a></li>
          </ul>
        </div>
      </nav>

      <main className="app-main">
        <DashboardRoadmap />
      </main>

      <footer className="app-footer">
        <p>&copy; 2025 Video Genius. All rights reserved.</p>
        <p>API: <a href={API_URL} target="_blank" rel="noopener noreferrer">
          {API_URL}
        </a></p>
      </footer>
    </div>
  )
}

export default App
