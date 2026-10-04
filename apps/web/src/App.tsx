import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { CreateShortPage } from './pages/CreateShortPage';
import { GenerateProgressPage } from './pages/GenerateProgressPage';
import { ResultPage } from './pages/ResultPage';
import { ProjectDetailPage } from './pages/ProjectDetailPage';
import { SettingsPage } from './pages/SettingsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-dark-950 text-slate-100 flex flex-col selection:bg-pink-500 selection:text-white">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/create" element={<CreateShortPage />} />
            <Route path="/project/:id" element={<ProjectDetailPage />} />
            <Route path="/project/:id/generate" element={<GenerateProgressPage />} />
            <Route path="/project/:id/result" element={<ResultPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
