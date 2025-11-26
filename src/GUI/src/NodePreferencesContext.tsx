import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

type NodeSize = 'large' | 'medium' | 'small';

interface NodePreferencesContextType {
  nodeSize: NodeSize;
  setNodeSize: (size: NodeSize) => void;
}

const NodePreferencesContext = createContext<NodePreferencesContextType | undefined>(undefined);

const STORAGE_KEY = 'textloom-node-size';

export const NodePreferencesProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [nodeSize, setNodeSizeState] = useState<NodeSize>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return (stored === 'medium' || stored === 'small' ? stored : 'large') as NodeSize;
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, nodeSize);
  }, [nodeSize]);

  const setNodeSize = (size: NodeSize) => {
    setNodeSizeState(size);
  };

  return (
    <NodePreferencesContext.Provider value={{ nodeSize, setNodeSize }}>
      {children}
    </NodePreferencesContext.Provider>
  );
};

export const useNodePreferences = (): NodePreferencesContextType => {
  const context = useContext(NodePreferencesContext);
  if (!context) {
    throw new Error('useNodePreferences must be used within NodePreferencesProvider');
  }
  return context;
};
