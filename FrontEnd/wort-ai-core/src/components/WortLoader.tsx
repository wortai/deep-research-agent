import React, { useState, useEffect, useRef, useMemo } from 'react';

interface WortLoaderProps {
  isProcessing: boolean;
  hasAgents: boolean;
  hasWriter?: boolean;
}

// ── Grid dimensions ──
const GRID_COLS = 40;
const GRID_ROWS = 8;
const DOT_SIZE = 3; // px
const DOT_GAP = 2;  // px
const CELL = DOT_SIZE + DOT_GAP; // 5px per cell

// WORT letter positions — 150 dots total (W:46, O:36, R:40, T:28)
// Layout: W(0-9) + gap(2) + O(12-19) + gap(2) + R(22-29) + gap(2) + T(32-39)
const WORT_POSITIONS: [number, number][] = [
  // ──── W (cols 0–9, 46 dots) ────
  [0, 0], [0, 1], [0, 8], [0, 9],
  [1, 0], [1, 1], [1, 8], [1, 9],
  [2, 0], [2, 1], [2, 8], [2, 9],
  [3, 0], [3, 1], [3, 8], [3, 9],
  [4, 0], [4, 1], [4, 8], [4, 9],
  [5, 0], [5, 1], [5, 8], [5, 9],
  [6, 0], [6, 1], [6, 8], [6, 9],
  [7, 0], [7, 1], [7, 8], [7, 9],
  [3, 4], [3, 5],
  [4, 4], [4, 5],
  [5, 3], [5, 4], [5, 5], [5, 6],
  [6, 2], [6, 3], [6, 6], [6, 7],
  [7, 2], [7, 7],

  // ──── O (cols 12–19, 36 dots) ────
  [0, 14], [0, 15], [0, 16], [0, 17],
  [7, 14], [7, 15], [7, 16], [7, 17],
  [1, 13], [1, 14], [1, 15], [1, 16], [1, 17], [1, 18],
  [6, 13], [6, 14], [6, 15], [6, 16], [6, 17], [6, 18],
  [2, 12], [2, 13], [2, 18], [2, 19],
  [3, 12], [3, 13], [3, 18], [3, 19],
  [4, 12], [4, 13], [4, 18], [4, 19],
  [5, 12], [5, 13], [5, 18], [5, 19],

  // ──── R (cols 22–29, 40 dots) ────
  [0, 22], [0, 23],
  [1, 22], [1, 23],
  [2, 22], [2, 23],
  [3, 22], [3, 23],
  [4, 22], [4, 23],
  [5, 22], [5, 23],
  [6, 22], [6, 23],
  [7, 22], [7, 23],
  [0, 24], [0, 25], [0, 26], [0, 27],
  [1, 24], [1, 25], [1, 26], [1, 27], [1, 28],
  [4, 24], [4, 25], [4, 26], [4, 27], [4, 28],
  [2, 27], [2, 28],
  [3, 27], [3, 28],
  [5, 26], [5, 27],
  [6, 27], [6, 28],
  [7, 28], [7, 29],

  // ──── T (cols 32–39, 28 dots) ────
  [0, 32], [0, 33], [0, 34], [0, 35], [0, 36], [0, 37], [0, 38], [0, 39],
  [1, 32], [1, 33], [1, 34], [1, 35], [1, 36], [1, 37], [1, 38], [1, 39],
  [2, 35], [2, 36],
  [3, 35], [3, 36],
  [4, 35], [4, 36],
  [5, 35], [5, 36],
  [6, 35], [6, 36],
  [7, 35], [7, 36],
];

// Square positions: 6×25 filled rectangle, centered in the 40-col grid
const SQUARE_POSITIONS: [number, number][] = (() => {
  const positions: [number, number][] = [];
  for (let row = 1; row <= 6; row++) {
    for (let col = 8; col <= 32; col++) {
      positions.push([row, col]);
    }
  }
  return positions;
})();

// ── Phase & pattern types ──
type Phase = 'idle' | 'session_start' | 'agents_active' | 'completing' | 'fading';
type PatternType = 'wave' | 'ripple' | 'vortex' | 'diagonal' | 'aurora' | 'cascade' | 'zigzag';

const PATTERNS: PatternType[] = ['wave', 'ripple', 'vortex', 'diagonal', 'aurora', 'cascade', 'zigzag'];
const PATTERN_DURATION_MS = 2400; // each pattern runs 2.4s before blending to the next
const BLEND_DURATION_MS = 900;    // crossfade between consecutive patterns
const MORPH_DURATION_MS = 800;    // morph CSS transition settle time
const FADE_DURATION_MS = 1000;    // final fade back to idle

// ── Surfaces (radial gradients = highlight → body → edge for depth; no blur) ──
type DotSurface = 'idle' | 'research' | 'writer';

const COLOR_IDLE = [170, 175, 185]; // Darker cool-grey for better base contrast
const COLOR_RESEARCH = [255, 110, 34]; // Brighter, more intense punchy green
const COLOR_WRITER = [224, 176, 32];

function getDotColor(surface: DotSurface, intensity: number): string {
  if (surface === 'idle' || intensity <= 0) {
    return `rgb(${COLOR_IDLE.join(',')})`;
  }
  const target = surface === 'writer' ? COLOR_WRITER : COLOR_RESEARCH;
  const rgb = COLOR_IDLE.map((base, i) =>
    Math.round(base + (target[i] - base) * intensity)
  );
  return `rgb(${rgb.join(',')})`;
}

// ── Organic multi-frequency wave ──
// Three superimposed sinusoids create water-like, non-repeating motion.
function organicWave(time: number, offset: number, speed = 1.0): number {
  const a = Math.sin(time * speed * 3.0 + offset);                       // primary
  const b = Math.sin(time * speed * 6.8 + offset * 1.6 + 0.8) * 0.38;  // harmonic
  const c = Math.sin(time * speed * 1.4 + offset * 0.4) * 0.22;         // slow swell
  return Math.max(0, (a + b + c) / 1.6); // normalized to [0, 1]
}

function easeInOutCubic(t: number): number {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// ── Pattern offset computation ──
// Maps each dot's [row, col] to a phase value used as the offset fed into the
// wave function. Spatial relationships create directional flows.
function computePatternOffsets(
  positions: [number, number][],
  pattern: PatternType
): number[] {
  const n = positions.length;

  switch (pattern) {
    case 'wave': {
      // Pure left-to-right horizontal sweep
      const cols = positions.map(([, c]) => c);
      const minC = Math.min(...cols), maxC = Math.max(...cols);
      return positions.map(([, c]) =>
        ((c - minC) / (maxC - minC || 1)) * Math.PI * 2
      );
    }

    case 'zigzag': {
      // Boustrophedon scan: left-right on even rows, right-left on odd
      const indexed = positions.map(([row, col], i) => ({ row, col, i }));
      indexed.sort((a, b) => {
        if (a.row !== b.row) return a.row - b.row;
        return a.row % 2 === 0 ? a.col - b.col : b.col - a.col;
      });
      const offsets = new Array<number>(n);
      indexed.forEach((item, rank) => {
        offsets[item.i] = (rank / n) * Math.PI * 2;
      });
      return offsets;
    }

    case 'diagonal': {
      // Dots sharing the same anti-diagonal (row+col) glow together
      const diagSums = positions.map(([r, c]) => r + c);
      const uniqueDiags = [...new Set(diagSums)].sort((a, b) => a - b);
      const diagMap = new Map(uniqueDiags.map((sum, i) => [sum, i]));
      const numDiags = uniqueDiags.length;
      return positions.map(([r, c]) =>
        ((diagMap.get(r + c) ?? 0) / numDiags) * Math.PI * 2
      );
    }

    case 'ripple': {
      // Concentric rings expanding from the centroid
      const centerR = positions.reduce((s, [r]) => s + r, 0) / n;
      const centerC = positions.reduce((s, [, c]) => s + c, 0) / n;
      const maxDist = Math.max(
        ...positions.map(([r, c]) => Math.sqrt((r - centerR) ** 2 + (c - centerC) ** 2))
      );
      return positions.map(([r, c]) => {
        const dist = Math.sqrt((r - centerR) ** 2 + (c - centerC) ** 2);
        return (dist / (maxDist || 1)) * Math.PI * 4; // two full ring cycles
      });
    }

    case 'vortex': {
      // Whirlpool: angular position around center, wound outward into a spiral
      const centerR = positions.reduce((s, [r]) => s + r, 0) / n;
      const centerC = positions.reduce((s, [, c]) => s + c, 0) / n;
      const maxDist = Math.max(
        ...positions.map(([r, c]) => Math.sqrt((r - centerR) ** 2 + (c - centerC) ** 2))
      );
      return positions.map(([r, c]) => {
        const angle = Math.atan2(r - centerR, c - centerC) + Math.PI; // 0..2π
        const dist = Math.sqrt((r - centerR) ** 2 + (c - centerC) ** 2);
        return angle + (dist / (maxDist || 1)) * Math.PI * 1.5;
      });
    }

    case 'cascade': {
      // Falling curtain: top-to-bottom with gentle column-wise shimmer
      return positions.map(([r, c]) => {
        const rowPhase = (r / (GRID_ROWS - 1)) * Math.PI * 2;
        const colShimmer = Math.sin(c * 0.7) * 0.5; // subtle lateral undulation
        return rowPhase + colShimmer;
      });
    }

    case 'aurora': {
      // Northern lights: horizontal bands with sinusoidal column undulation
      const rows = positions.map(([r]) => r);
      const minR = Math.min(...rows), maxR = Math.max(...rows);
      return positions.map(([r, c]) => {
        const rowPhase = ((r - minR) / (maxR - minR || 1)) * Math.PI * 2;
        const colUndulate = Math.sin(c * 0.35 + r * 0.2) * 0.9;
        return rowPhase + colUndulate;
      });
    }
  }
}

// ── Component ──

const WortLoader: React.FC<WortLoaderProps> = ({
  isProcessing,
  hasAgents,
  hasWriter = false,
}) => {
  const [phase, setPhase] = useState<Phase>('idle');
  const [tick, setTick] = useState(0);

  const prevProcessingRef = useRef(false);
  const prevHasAgentsRef = useRef(false);
  const phaseStartRef = useRef(Date.now());
  const phaseRef = useRef<Phase>('idle');
  const rafRef = useRef(0);
  const patternTimerRef = useRef<ReturnType<typeof setTimeout>>();

  // Pattern blend state in refs — read each frame, no re-render needed
  const patternTransitionRef = useRef({ fromIndex: 0, toIndex: 0, startTime: Date.now() });

  const activeSurface: DotSurface = hasWriter ? 'writer' : 'research';

  const dotPairs = useMemo(
    () => WORT_POSITIONS.map((wort, i) => ({ wort, square: SQUARE_POSITIONS[i] })),
    []
  );

  // Pre-compute pattern offsets for both shape sets once (7 patterns × 2 shapes)
  const wortPatternOffsets = useMemo(
    () => PATTERNS.map(p => computePatternOffsets(WORT_POSITIONS, p)),
    []
  );
  const squarePatternOffsets = useMemo(
    () => PATTERNS.map(p => computePatternOffsets(SQUARE_POSITIONS, p)),
    []
  );

  // ── Phase transitions ──
  useEffect(() => {
    const wasProcessing = prevProcessingRef.current;
    const hadAgents = prevHasAgentsRef.current;
    prevProcessingRef.current = isProcessing;
    prevHasAgentsRef.current = hasAgents;

    if (isProcessing && !wasProcessing) {
      phaseRef.current = 'session_start';
      setPhase('session_start');
      phaseStartRef.current = Date.now();
    } else if (isProcessing && hasAgents && !hadAgents) {
      if (phaseRef.current !== 'agents_active') {
        phaseRef.current = 'agents_active';
        setPhase('agents_active');
        phaseStartRef.current = Date.now();
      }
    } else if (isProcessing && !hasAgents && hadAgents) {
      phaseRef.current = 'session_start';
      setPhase('session_start');
      phaseStartRef.current = Date.now();
    } else if (!isProcessing && wasProcessing) {
      phaseRef.current = 'completing';
      setPhase('completing');
      phaseStartRef.current = Date.now();
    }
  }, [isProcessing, hasAgents]);

  // ── Pattern cycling with smooth crossfade ──
  useEffect(() => {
    if (phase !== 'session_start' && phase !== 'agents_active') return;

    patternTransitionRef.current = { fromIndex: 0, toIndex: 0, startTime: Date.now() };

    const cycle = () => {
      const currentTo = patternTransitionRef.current.toIndex;
      const nextIndex = (currentTo + 1) % PATTERNS.length;
      patternTransitionRef.current = { fromIndex: currentTo, toIndex: nextIndex, startTime: Date.now() };
      patternTimerRef.current = setTimeout(cycle, PATTERN_DURATION_MS);
    };
    patternTimerRef.current = setTimeout(cycle, PATTERN_DURATION_MS);
    return () => { if (patternTimerRef.current) clearTimeout(patternTimerRef.current); };
  }, [phase]);

  // ── Phase duration timers: completing → fading → idle ──
  useEffect(() => {
    if (phase === 'completing') {
      const timer = setTimeout(() => {
        if (phaseRef.current === 'completing') {
          phaseRef.current = 'fading';
          setPhase('fading');
          phaseStartRef.current = Date.now();
        }
      }, MORPH_DURATION_MS);
      return () => clearTimeout(timer);
    }
    if (phase === 'fading') {
      const timer = setTimeout(() => {
        if (phaseRef.current === 'fading') {
          phaseRef.current = 'idle';
          setPhase('idle');
        }
      }, FADE_DURATION_MS);
      return () => clearTimeout(timer);
    }
  }, [phase]);

  // ── Animation loop ──
  useEffect(() => {
    if (phase === 'idle') {
      // 20fps is enough for gentle breathing — saves battery vs full RAF
      const interval = setInterval(() => setTick(t => t + 1), 50);
      return () => clearInterval(interval);
    }
    const animate = () => {
      setTick(t => t + 1);
      rafRef.current = requestAnimationFrame(animate);
    };
    rafRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafRef.current);
  }, [phase]);

  // ── Compute each dot's position, opacity, and surface every frame ──
  const dotData = useMemo(() => {
    const now = Date.now();
    const elapsed = now - phaseStartRef.current;
    const time = tick * 0.016; // approximate seconds

    // Cross-blend between two adjacent patterns
    const { fromIndex, toIndex, startTime } = patternTransitionRef.current;
    const blendRaw = Math.min(1, (now - startTime) / BLEND_DURATION_MS);
    const blendFraction = easeInOutCubic(blendRaw);

    const blendedOffset = (patternOffsets: number[][], i: number): number => {
      const from = patternOffsets[fromIndex][i];
      const to = patternOffsets[toIndex][i];
      return from + (to - from) * blendFraction;
    };

    return dotPairs.map((pair, i) => {
      const [wortRow, wortCol] = pair.wort;
      const [sqRow, sqCol] = pair.square;

      let targetRow: number;
      let targetCol: number;
      let opacity: number;
      let background: string;
      let glow: number;

      switch (phase) {
        case 'idle': {
          targetRow = wortRow;
          targetCol = wortCol;
          opacity = 1;
          const breath = Math.sin(time * 0.8 + (wortRow + wortCol) * 0.4) * 0.08;
          const sparkle = Math.abs(Math.sin(time * 4.0 + wortCol * 0.9 + wortRow * 1.3)) * 0.05;
          const brightness = 1 + breath + sparkle;
          const [r, g, b] = COLOR_IDLE.map(c => Math.round(Math.min(255, c * brightness)));
          background = `rgb(${r},${g},${b})`;
          glow = 0;
          break;
        }

        case 'session_start': {
          targetRow = wortRow;
          targetCol = wortCol;
          const offset = blendedOffset(wortPatternOffsets, i);
          const waveIntensity = organicWave(time, offset);
          opacity = 1;
          background = getDotColor(activeSurface, waveIntensity);
          glow = waveIntensity;
          break;
        }

        case 'agents_active': {
          targetRow = sqRow;
          targetCol = sqCol;
          const offset = blendedOffset(squarePatternOffsets, i);
          const waveIntensity = organicWave(time, offset);
          opacity = 1;
          background = getDotColor(activeSurface, waveIntensity);
          glow = waveIntensity;
          break;
        }

        case 'completing': {
          targetRow = wortRow;
          targetCol = wortCol;
          const waveIntensity = organicWave(time, (wortRow + wortCol) * 0.4, 0.6);
          opacity = 1;
          background = getDotColor(activeSurface, waveIntensity);
          glow = waveIntensity * 0.6;
          break;
        }

        case 'fading': {
          targetRow = wortRow;
          targetCol = wortCol;
          const progress = Math.min(1, elapsed / FADE_DURATION_MS);
          const eased = easeInOutCubic(progress);
          opacity = 1 - eased;
          background = getDotColor(activeSurface, 0);
          glow = 0;
          break;
        }

        default:
          targetRow = wortRow;
          targetCol = wortCol;
          opacity = 1;
          background = getDotColor('idle', 0);
          glow = 0;
      }

      return {
        key: i,
        left: targetCol * CELL,
        top: targetRow * CELL,
        opacity,
        background,
        glow,
      };
    });
    // patternTransitionRef is a ref — tick drives re-computation each frame
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dotPairs, phase, tick, activeSurface, wortPatternOffsets, squarePatternOffsets]);

  return (
    <div className="flex items-center justify-center">
      <div
        className="relative"
        style={{
          width: `${GRID_COLS * CELL}px`,
          height: `${GRID_ROWS * CELL}px`,
        }}
      >
        {dotData.map((dot) => (
          <div
            key={dot.key}
            style={{
              position: 'absolute',
              left: `${dot.left}px`,
              top: `${dot.top}px`,
              width: `${DOT_SIZE}px`,
              height: `${DOT_SIZE}px`,
              background: dot.background,
              opacity: dot.opacity,
              borderRadius: '50%',
              boxShadow: dot.glow > 0
                ? `0 0 ${2 + dot.glow * 4}px ${dot.background}`
                : 'none',
              transition:
                'left 0.8s cubic-bezier(0.4, 0, 0.2, 1), ' +
                'top 0.8s cubic-bezier(0.4, 0, 0.2, 1), ' +
                'opacity 0.35s ease',
              willChange: 'left, top, opacity',
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default WortLoader;
