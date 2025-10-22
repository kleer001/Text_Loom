// src/GUI/hooks/usePolling.ts

import { useEffect, useRef } from 'react';

export const usePolling = (callback: () => void, interval: number = 2000) => {
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        savedCallback.current();
      }
    };

    const tick = () => {
      if (!document.hidden) {
        savedCallback.current();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    const id = setInterval(tick, interval);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      clearInterval(id);
    };
  }, [interval]);
};