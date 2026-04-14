import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';

/**
 * Lightweight context to bridge processing state between ChatWorkspace (writer)
 * and WortHeader (reader). These are sibling components in Index.tsx that cannot
 * share state via props without a shared ancestor provider.
 */

interface ProcessingState {
  isProcessing: boolean;
  hasAgents: boolean;
  hasWriter: boolean;
}

interface ProcessingContextValue extends ProcessingState {
  updateProcessingState: (partial: Partial<ProcessingState>) => void;
}

const ProcessingStateContext = createContext<ProcessingContextValue>({
  isProcessing: false,
  hasAgents: false,
  hasWriter: false,
  updateProcessingState: () => {},
});

export const useProcessingState = () => useContext(ProcessingStateContext);

export function ProcessingStateProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<ProcessingState>({
    isProcessing: false,
    hasAgents: false,
    hasWriter: false,
  });

  const updateProcessingState = useCallback((partial: Partial<ProcessingState>) => {
    setState(prev => {
      const next = { ...prev, ...partial };
      if (
        next.isProcessing === prev.isProcessing &&
        next.hasAgents === prev.hasAgents &&
        next.hasWriter === prev.hasWriter
      ) {
        return prev;
      }
      return next;
    });
  }, []);

  return (
    <ProcessingStateContext.Provider value={{ ...state, updateProcessingState }}>
      {children}
    </ProcessingStateContext.Provider>
  );
}
