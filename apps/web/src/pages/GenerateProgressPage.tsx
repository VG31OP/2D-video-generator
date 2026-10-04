import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchProject, subscribeToProjectProgress } from '../services/api';
import { ProgressTimeline } from '../components/ProgressTimeline';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const GenerateProgressPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('Initializing');
  const [stageMessage, setStageMessage] = useState('Connecting to generation engine...');
  const [logs, setLogs] = useState<string[]>([]);
  const [providers, setProviders] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    // Fetch initial status
    fetchProject(id)
      .then((project) => {
        if (project.status === 'Completed') {
          navigate(`/project/${id}/result`, { replace: true });
          return;
        }
        if (project.job) {
          setProgress(project.job.progress_percent || 5);
          setCurrentStage(project.job.current_stage || 'Planning');
          setStageMessage(project.job.stage_message || 'Working on your cartoon short...');
          setLogs(project.job.logs || []);
        }
        if (project.metadata?.providers) {
          setProviders(project.metadata.providers);
        }
      })
      .catch((err) => {
        setError(err.message || 'Failed to load project status');
      });

    // Subscribe to real-time WebSocket updates
    const unsubscribe = subscribeToProjectProgress(id, (data) => {
      if (data.stage === 'Failed' || data.error) {
        setError(data.error || 'Generation failed');
        return;
      }
      if (data.progress !== undefined) {
        setProgress(data.progress);
      }
      if (data.stage) {
        setCurrentStage(data.stage);
      }
      if (data.message) {
        setStageMessage(data.message);
        setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${data.message}`]);
      }
      if (data.providers) {
        setProviders(data.providers);
      }
      if (data.progress >= 100 || data.stage === 'Completed') {
        setTimeout(() => {
          navigate(`/project/${id}/result`, { replace: true });
        }, 1500);
      }
    });

    // Fallback polling every 3 seconds in case WebSocket disconnects
    const pollInterval = setInterval(() => {
      fetchProject(id).then((p) => {
        if (p.status === 'Completed') {
          navigate(`/project/${id}/result`, { replace: true });
        } else if (p.status === 'Failed') {
          setError(p.error_message || 'Generation failed');
        } else if (p.job) {
          setProgress(p.job.progress_percent);
          setCurrentStage(p.job.current_stage);
          setStageMessage(p.job.stage_message);
          if (p.job.logs) setLogs(p.job.logs);
          if (p.metadata?.providers) setProviders(p.metadata.providers);
        }
      });
    }, 3000);

    return () => {
      unsubscribe();
      clearInterval(pollInterval);
    };
  }, [id, navigate]);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 space-y-8">
      {error ? (
        <div className="glass-panel rounded-3xl p-8 text-center space-y-4 max-w-lg mx-auto border-red-500/40">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto" />
          <h2 className="text-xl font-bold text-white">Generation Issue</h2>
          <p className="text-xs text-red-300">{error}</p>
          <button
            onClick={() => navigate('/create')}
            className="px-6 py-2.5 rounded-xl bg-purple-600 text-white text-xs font-semibold hover:bg-purple-500 transition"
          >
            Try Again
          </button>
        </div>
      ) : (
        <ProgressTimeline
          progress={progress}
          currentStage={currentStage}
          stageMessage={stageMessage}
          logs={logs}
          providers={providers}
        />
      )}
    </div>
  );
};
