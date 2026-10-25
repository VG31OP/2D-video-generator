import { useState, useEffect, useRef, useCallback } from 'react';
import { fetchInstagramStatus, launchInstagramBrowserLogin } from '../services/api';

export interface InstagramProfile {
  username: string;
  full_name: string;
  follower_count: number;
  following_count: number;
  media_count: number;
  profile_pic_url: string;
  biography: string;
  is_verified: boolean;
}

export interface InstagramStatusResponse {
  authenticated: boolean;
  profile?: InstagramProfile;
  message?: string;
  error?: string;
}

export function useInstagramLoginPolling() {
  const [instaStatus, setInstaStatus] = useState<InstagramStatusResponse | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [launchingLogin, setLaunchingLogin] = useState(false);

  const intervalRef = useRef<number | null>(null);
  const timeoutRef = useRef<number | null>(null);

  const clearTimers = useCallback(() => {
    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (timeoutRef.current !== null) {
      window.clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setIsPolling(false);
  }, []);

  const refreshStatus = useCallback(async () => {
    try {
      const status = await fetchInstagramStatus();
      setInstaStatus(status);
      return status;
    } catch (err) {
      console.warn('Failed to fetch Instagram status:', err);
      return null;
    }
  }, []);

  const startLoginCapture = useCallback(async () => {
    try {
      setLaunchingLogin(true);
      await launchInstagramBrowserLogin();
      alert('Instagram login browser window launched! Log into your account there; your session will be saved automatically.');

      clearTimers();
      setIsPolling(true);

      // Poll every 3 seconds for up to 300 seconds (matches login timeout)
      intervalRef.current = window.setInterval(async () => {
        try {
          const status = await fetchInstagramStatus();
          if (status) {
            setInstaStatus(status);
            if (status.authenticated) {
              clearTimers();
            }
          }
        } catch (err) {
          console.warn('Polling check error:', err);
        }
      }, 3000);

      timeoutRef.current = window.setTimeout(() => {
        clearTimers();
      }, 300000);
    } catch (err: any) {
      alert(err.message || 'Failed to launch Instagram login');
    } finally {
      setLaunchingLogin(false);
    }
  }, [clearTimers]);

  useEffect(() => {
    refreshStatus();
    return () => {
      clearTimers();
    };
  }, [refreshStatus, clearTimers]);

  return {
    instaStatus,
    setInstaStatus,
    refreshStatus,
    startLoginCapture,
    isPolling,
    launchingLogin,
    clearTimers,
  };
}
