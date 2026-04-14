import { memo } from "react";
import { C } from "./tokens";

function SolarSystemOInner() {
  return (
    <div className="relative w-20 h-20 sm:w-24 sm:h-24 md:w-32 md:h-32 flex items-center justify-center shrink-0">
      <div className="w-4 h-4 md:w-5 md:h-5 bg-[#F4D35E] rounded-full shadow-[0_0_12px_rgba(244,211,94,0.4)] z-10" />

      <div
        className="absolute w-[25%] h-[25%] border border-dashed border-[#1A3C2B]/20 rounded-full orbit-planet"
        style={{ animationDuration: "6s" }}
      >
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: "conic-gradient(from 270deg, transparent 80%, rgba(122, 109, 93, 0.15) 100%)",
            WebkitMaskImage: "radial-gradient(closest-side, transparent 96%, black 97%)",
            maskImage: "radial-gradient(closest-side, transparent 96%, black 97%)",
          }}
        />
        <div
          className="absolute -top-[1.25px] left-1/2 -translate-x-1/2 w-[2.5px] h-[2.5px] rounded-full overflow-hidden"
          style={{ background: "radial-gradient(circle at 70% 30%, rgba(255,255,255,0.15), transparent), #7A6D5D" }}
        />
      </div>

      <div
        className="absolute w-[35%] h-[35%] border border-dashed border-[#1A3C2B]/20 rounded-full orbit-planet"
        style={{ animationDuration: "8s", animationDirection: "reverse" }}
      >
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: "conic-gradient(from 0deg, rgba(244, 216, 159, 0.15) 0%, transparent 20%)",
            WebkitMaskImage: "radial-gradient(closest-side, transparent 96%, black 97%)",
            maskImage: "radial-gradient(closest-side, transparent 96%, black 97%)",
          }}
        />
        <div
          className="absolute -top-[1.5px] left-1/2 -translate-x-1/2 w-[3px] h-[3px] rounded-full"
          style={{ background: "conic-gradient(from 0deg, #F4D89F, #EED291 25%, #F4D89F 50%, #EED291 75%, #F4D89F)" }}
        />
      </div>

      <div
        className="absolute w-[50%] h-[50%] border border-dashed border-[#1A3C2B]/20 rounded-full orbit-planet"
        style={{ animationDuration: "10s" }}
      >
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: "conic-gradient(from 270deg, transparent 80%, rgba(30, 120, 60, 0.2) 100%)",
            WebkitMaskImage: "radial-gradient(closest-side, transparent 96%, black 97%)",
            maskImage: "radial-gradient(closest-side, transparent 96%, black 97%)",
          }}
        />
        <div
          className="absolute -top-[1.75px] left-1/2 -translate-x-1/2 w-[3.5px] h-[3.5px] rounded-full overflow-hidden"
          style={{ background: "radial-gradient(circle at 100% 50%, rgba(30,120,60,0.5) 40%, transparent 60%), #2D7A4F" }}
        />
      </div>

      <div
        className="absolute w-[65%] h-[65%] border border-dashed border-[#1A3C2B]/20 rounded-full orbit-planet"
        style={{ animationDuration: "12s", animationDirection: "reverse" }}
      >
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: "conic-gradient(from 0deg, rgba(184, 92, 60, 0.15) 0%, transparent 20%)",
            WebkitMaskImage: "radial-gradient(closest-side, transparent 97%, black 98%)",
            maskImage: "radial-gradient(closest-side, transparent 97%, black 98%)",
          }}
        />
        <div
          className="absolute -top-[1.75px] left-1/2 -translate-x-1/2 w-[3.5px] h-[3.5px] rounded-full"
          style={{ background: C.mars }}
        />
      </div>

      <div
        className="absolute w-[80%] h-[80%] border border-dashed border-[#1A3C2B]/20 rounded-full orbit-planet"
        style={{ animationDuration: "14s" }}
      >
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: "conic-gradient(from 270deg, transparent 80%, rgba(201, 145, 92, 0.15) 100%)",
            WebkitMaskImage: "radial-gradient(closest-side, transparent 97%, black 98%)",
            maskImage: "radial-gradient(closest-side, transparent 97%, black 98%)",
          }}
        />
        <div className="absolute -top-[2.5px] left-1/2 -translate-x-1/2 w-[5px] h-[5px] bg-[#C9915C] rounded-full" />
      </div>

      <div
        className="absolute w-[95%] h-[95%] border border-dashed border-[#1A3C2B]/20 rounded-full orbit-planet"
        style={{ animationDuration: "16s", animationDirection: "reverse" }}
      >
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: "conic-gradient(from 0deg, rgba(232, 217, 184, 0.15) 0%, transparent 20%)",
            WebkitMaskImage: "radial-gradient(closest-side, transparent 97%, black 98%)",
            maskImage: "radial-gradient(closest-side, transparent 97%, black 98%)",
          }}
        />
        <div className="absolute -top-[2.25px] left-1/2 -translate-x-1/2 flex items-center justify-center">
          <div className="w-[4.5px] h-[4.5px] rounded-full z-10" style={{ background: C.sand }} />
          <div
            className="absolute w-[9px] h-[9px] border border-dashed border-[#D4B896]/30 rounded-full"
            style={{ transform: "rotateX(70deg)" }}
          />
        </div>
      </div>
    </div>
  );
}

export const SolarSystemO = memo(SolarSystemOInner);
