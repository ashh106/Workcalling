import { useCallback, useRef, useState } from "react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function ResizableSurface({
  children,
  initial = { w: 720, h: 460 },
  min = { w: 420, h: 260 },
  max = { w: 1200, h: 820 },
  className,
}: {
  children: ReactNode;
  initial?: { w: number; h: number };
  min?: { w: number; h: number };
  max?: { w: number; h: number };
  className?: string;
}) {
  const [size, setSize] = useState(initial);
  const start = useRef<{ x: number; y: number; w: number; h: number } | null>(null);

  const onPointerDown = useCallback((e: React.PointerEvent) => {
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
    start.current = { x: e.clientX, y: e.clientY, w: size.w, h: size.h };
  }, [size]);

  const onPointerMove = useCallback((e: React.PointerEvent) => {
    if (!start.current) return;
    const dx = e.clientX - start.current.x;
    const dy = e.clientY - start.current.y;
    setSize({
      w: Math.max(min.w, Math.min(max.w, start.current.w + dx)),
      h: Math.max(min.h, Math.min(max.h, start.current.h + dy)),
    });
  }, [min, max]);

  const onPointerUp = useCallback((e: React.PointerEvent) => {
    (e.target as HTMLElement).releasePointerCapture(e.pointerId);
    start.current = null;
  }, []);

  return (
    <div
      className={cn(
        "surface-glass rounded-2xl relative overflow-hidden glass-appear",
        className,
      )}
      style={{ width: size.w, height: size.h }}
    >
      {children}
      <div
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        className="absolute right-2 bottom-2 w-5 h-5 cursor-nwse-resize opacity-40 hover:opacity-80 transition-opacity"
        aria-label="Resize"
      >
        <svg viewBox="0 0 16 16" className="w-full h-full text-[hsl(var(--surface-foreground))]">
          <path d="M14 6 L6 14 M14 10 L10 14 M14 14 L14 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </div>
    </div>
  );
}
