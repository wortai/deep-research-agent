import React, { useState } from 'react';
import { AlertTriangle, RefreshCw, XCircle, Code, List, FileWarning } from 'lucide-react';

export interface AgentErrorData {
  message: string;
  raw_output?: string;
  error_details?: string;
  traceback?: string;
  section_id?: string;
}

interface LLMCatchErrorProps {
  errorData: AgentErrorData;
  onRetry: () => void;
  onCancel?: () => void;
}

export const LLMCatchError: React.FC<LLMCatchErrorProps> = ({ errorData, onRetry, onCancel }) => {
  const [activeTab, setActiveTab] = useState<'details' | 'raw_output' | 'traceback'>('details');

  return (
    <div className="w-full flex justify-center py-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="w-[85%] max-w-4xl bg-[#F7F7F5] border border-[#FF8C69]/40 rounded-[2px] shadow-sm flex flex-col relative overflow-hidden">
        
        {/* Top Header */}
        <div className="flex items-center justify-between bg-[#FF8C69]/10 px-4 py-3 border-b border-[#FF8C69]/20">
          <div className="flex items-center gap-3">
            <AlertTriangle size={18} className="text-[#FF8C69]" />
            <h3 className="font-mono text-[11px] uppercase tracking-[0.15em] font-semibold text-[#FF8C69]">
              System Interruption: LLM Failure
            </h3>
          </div>
          {onCancel && (
            <button onClick={onCancel} className="text-[#3A3A38]/50 hover:text-[#3A3A38] transition-colors">
              <XCircle size={16} />
            </button>
          )}
        </div>

        {/* Content Area */}
        <div className="p-6 flex flex-col gap-6">
          <div className="flex flex-col gap-2">
            <h2 className="text-xl font-bold font-space-grotesk text-[#1A3C2B]">
              Analysis Pipeline Halted
            </h2>
            <p className="text-sm font-sans text-[#1A3C2B]/80">
              {errorData.message || "An unrecoverable extraction or hallucination error occurred within the language model process. Read the technical logs below to understand the deviation."}
            </p>
          </div>

          {/* Dev Tabs */}
          <div className="flex flex-col border border-[#3A3A38]/20 rounded-[2px] overflow-hidden">
            <div className="flex items-center bg-black/5 border-b border-[#3A3A38]/20">
              <button 
                onClick={() => setActiveTab('details')}
                className={`flex-1 py-2 font-mono text-[10px] uppercase tracking-[0.1em] transition-colors flex items-center justify-center gap-2 ${activeTab === 'details' ? 'bg-white text-[#1A3C2B] font-bold' : 'text-[#3A3A38]/60 hover:bg-white/50'}`}
              >
                <List size={12} /> Log
              </button>
              <div className="w-[1px] h-full bg-[#3A3A38]/20" />
              <button 
                onClick={() => setActiveTab('raw_output')}
                className={`flex-1 py-2 font-mono text-[10px] uppercase tracking-[0.1em] transition-colors flex items-center justify-center gap-2 ${activeTab === 'raw_output' ? 'bg-white text-[#1A3C2B] font-bold' : 'text-[#3A3A38]/60 hover:bg-white/50'}`}
              >
                <FileWarning size={12} /> Raw Output
              </button>
              <div className="w-[1px] h-full bg-[#3A3A38]/20" />
              <button 
                onClick={() => setActiveTab('traceback')}
                className={`flex-1 py-2 font-mono text-[10px] uppercase tracking-[0.1em] transition-colors flex items-center justify-center gap-2 ${activeTab === 'traceback' ? 'bg-white text-[#1A3C2B] font-bold' : 'text-[#3A3A38]/60 hover:bg-white/50'}`}
              >
                <Code size={12} /> Traceback
              </button>
            </div>
            
            <div className="bg-white p-4 text-[12px] font-mono whitespace-pre-wrap overflow-y-auto max-h-64 custom-scrollbar text-[#3A3A38] leading-relaxed">
              {activeTab === 'details' && (errorData.error_details || "No specific details provided for this event.")}
              {activeTab === 'raw_output' && (errorData.raw_output || "No raw output recorded by the catch error.")}
              {activeTab === 'traceback' && (errorData.traceback || "No traceback context available.")}
            </div>
          </div>

          {/* Action Row */}
          <div className="flex items-center justify-end mt-2">
            <button 
              onClick={onRetry}
              className="flex items-center gap-2 px-6 py-2.5 bg-[#1A3C2B] hover:bg-black text-[#F7F7F5] font-mono text-[11px] uppercase tracking-[0.15em] transition-colors rounded-[2px]"
            >
              <RefreshCw size={14} />
              Retry Checkpoint
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
