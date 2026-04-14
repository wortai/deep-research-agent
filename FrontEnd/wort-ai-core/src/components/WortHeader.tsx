import React from 'react';
import { Link } from 'react-router-dom';
import WortLoader from './WortLoader';
import { useProcessingState } from '@/hooks/useProcessingState';
import { useAuth } from '@/lib/auth';
import { ROUTES } from '@/lib/routes';

const WortHeader = () => {
  const { user, isAuthenticated } = useAuth();
  const credits = isAuthenticated && user ? user.credits : null;
  const { isProcessing, hasAgents, hasWriter } = useProcessingState();

  return (
    <header className="border-b border-hairline sticky top-0 bg-background z-50 flex-shrink-0">
      <div className="w-full mx-auto px-2 sm:px-4 h-14 sm:h-16 flex items-center justify-between relative">
        {/* Left Section - Logo & About */}
        <div className="flex items-center gap-2 sm:gap-4">
          <Link
            to={ROUTES.home}
            className="w-7 h-7 sm:w-8 sm:h-8 bg-primary flex items-center justify-center shrink-0"
            title="WORT home"
          >
            <span className="text-primary-foreground font-display font-bold text-sm sm:text-lg">W</span>
          </Link>
          <Link
            to={ROUTES.about}
            className="font-mono text-[9px] sm:text-[10px] uppercase tracking-widest text-primary/70 hover:text-primary transition-colors hidden xs:inline"
          >
            About
          </Link>
        </div>

        {/* Center - Loader (hidden on very small screens) */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-0 select-none hidden sm:block">
          <WortLoader
            isProcessing={isProcessing}
            hasAgents={hasAgents}
            hasWriter={hasWriter}
          />
        </div>

        {/* Right Section - Credits */}
        <div className="flex items-center gap-1 sm:gap-2">
          {/* Credits icon - smaller on mobile */}
          <div className="w-4 h-4 sm:w-6 sm:h-6 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
              <g stroke="#1A3C2B" strokeWidth="0.5" opacity="0.6">
                <line x1="4" y1="12" x2="9" y2="6" />
                <line x1="4" y1="12" x2="9" y2="12" />
                <line x1="4" y1="12" x2="9" y2="18" />

                <line x1="9" y1="6" x2="15" y2="6" />
                <line x1="9" y1="6" x2="15" y2="12" />
                <line x1="9" y1="6" x2="15" y2="18" />
                <line x1="9" y1="12" x2="15" y2="6" />
                <line x1="9" y1="12" x2="15" y2="12" />
                <line x1="9" y1="12" x2="15" y2="18" />
                <line x1="9" y1="18" x2="15" y2="6" />
                <line x1="9" y1="18" x2="15" y2="12" />
                <line x1="9" y1="18" x2="15" y2="18" />

                <line x1="15" y1="6" x2="20" y2="12" />
                <line x1="15" y1="12" x2="20" y2="12" />
                <line x1="15" y1="18" x2="20" y2="12" />
              </g>
              <g fill="#1A3C2B">
                <circle cx="4" cy="12" r="1.5" />
                <circle cx="9" cy="6" r="1.5" />
                <circle cx="9" cy="12" r="1.5" />
                <circle cx="9" cy="18" r="1.5" />
                <circle cx="15" cy="6" r="1.5" />
                <circle cx="15" cy="12" r="1.5" />
                <circle cx="15" cy="18" r="1.5" />
                <circle cx="20" cy="12" r="1.5" />
              </g>
            </svg>
          </div>
          <style>
            {`
              @import url('https://fonts.googleapis.com/css2?family=DotGothic16&display=swap');
            `}
          </style>
          <span
            className="text-[10px] sm:text-[13px] tracking-wider select-none uppercase tracking-[0.1em] flex items-center gap-[2px] sm:gap-[4px] mt-[1px]"
            style={{ fontFamily: "'Bitcount Mono Double Book Circle', 'DotGothic16', monospace", color: "#1A3C2B" }}
          >
            <span className="hidden xs:inline">CREDITS</span>
            <span className="text-[#FF8C69]" style={{ letterSpacing: "normal" }}>{credits !== null ? Number(credits).toFixed(2) : "--"}</span>
          </span>
        </div>

      </div>
    </header>
  );
};

export default WortHeader;
