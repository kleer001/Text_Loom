import React, { createContext, useContext, useState, useCallback } from 'react';

interface SelectionContextValue {
  selectedNodePaths: string[];
  selectNode: (path: string, multi?: boolean) => void;
  clearSelection: () => void;
}

const SelectionContext = createContext<SelectionContextValue | null>(null);

export const SelectionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [selectedNodePaths, setSelectedNodePaths] = useState<string[]>([]);

  const selectNode = useCallback((path: string, multi = false) => {
    setSelectedNodePaths(prev => {
      if (multi) {
        return prev.includes(path) ? prev.filter(p => p !== path) : [...prev, path];
      }
      return [path];
    });
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedNodePaths([]);
  }, []);

  return (
    <SelectionContext.Provider value={{ selectedNodePaths, selectNode, clearSelection }}>
      {children}
    </SelectionContext.Provider>
  );
};

export const useSelection = () => {
  const ctx = useContext(SelectionContext);
  if (!ctx) throw new Error('useSelection must be used within SelectionProvider');
  return ctx;
};