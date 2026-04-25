import { useState } from 'react';
import Dashboard from './pages/Dashboard';
import SystemHealth from './components/SystemHealth';
import EmailScan from './components/EmailScan';
import TestLab from './pages/TestLab';
import { LayoutDashboard, Activity, Mail, FlaskConical } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState(null);

  const handleEmailAnalyze = (data) => {
    setDashboardData(data);
    setActiveTab('dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white font-sans">
      {/* Navigation Bar */}
      <nav className="bg-gray-800 border-b border-gray-700 px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="font-bold text-xl">U</span>
          </div>
          <span className="text-xl font-bold tracking-tight">URL Threat Analyzer <span className="text-xs bg-gray-700 px-2 py-0.5 rounded text-gray-400 ml-2">v1.2</span></span>
        </div>

        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('email')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition ${activeTab === 'email' ? 'bg-blue-600' : 'hover:bg-gray-700 text-gray-400'}`}
          >
            <Mail size={18} />
            Email Scan
          </button>
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition ${activeTab === 'dashboard' ? 'bg-blue-600' : 'hover:bg-gray-700 text-gray-400'}`}
          >
            <LayoutDashboard size={18} />
            Analyzer
          </button>
          <button
            onClick={() => setActiveTab('health')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition ${activeTab === 'health' ? 'bg-blue-600' : 'hover:bg-gray-700 text-gray-400'}`}
          >
            <Activity size={18} />
            System Health
          </button>
          <button
            onClick={() => setActiveTab('testlab')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition ${activeTab === 'testlab' ? 'bg-purple-600' : 'hover:bg-gray-700 text-gray-400'}`}
          >
            <FlaskConical size={18} />
            Test Lab
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto py-8">
        {activeTab === 'dashboard' && <Dashboard initialData={dashboardData} />}
        {activeTab === 'email' && <EmailScan onAnalyze={handleEmailAnalyze} />}
        {activeTab === 'health' && <SystemHealth />}
        {activeTab === 'testlab' && <TestLab />}
      </main>
    </div>
  );
}

export default App;
