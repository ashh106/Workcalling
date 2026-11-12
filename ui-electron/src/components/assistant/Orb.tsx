import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

type Mode = "idle" | "voice";

export function Orb({
  size = 64,
  mode = "idle",
  onClick,
  onDoubleClick,
}: {
  size?: number;
  mode?: Mode;
  onClick?: () => void;
  onDoubleClick?: () => void;
}) {
  return (
    <motion.button
      layoutId="assistant-orb"
      onClick={onClick}
      onDoubleClick={onDoubleClick}
      whileHover={{ scale: 1.08 }}
      whileTap={{ scale: 0.92 }}
      className={cn(
        "relative rounded-full orb-gradient cursor-pointer outline-none focus-visible:ring-4 focus-visible:ring-[hsl(var(--primary)/0.4)]",
        mode === "voice" && "animate-orb-pulse",
      )}
      style={{ width: size, height: size }}
      aria-label="Assistant orb"
    >
      {/* Inner shine layer */}
      <span
        className={cn(
          "absolute inset-0 rounded-full",
          mode === "idle" && "animate-orb-breathe orb-gradient",
        )}
      />
      {/* Outer glow halo */}
      <span
        className="absolute -inset-3 rounded-full opacity-30 blur-xl"
        style={{ background: "radial-gradient(circle, hsl(var(--primary-glow) / 0.6), transparent 70%)" }}
      />
      {/* Voice mode ripples */}
      {mode === "voice" && (
        <>
          <span className="absolute -inset-2 rounded-full border-2 border-[hsl(var(--primary-glow)/0.5)] animate-ring-ripple" />
          <span className="absolute -inset-2 rounded-full border-2 border-[hsl(var(--primary-glow)/0.5)] animate-ring-ripple" style={{ animationDelay: "0.5s" }} />
          <span className="absolute -inset-2 rounded-full border border-[hsl(var(--primary-glow)/0.3)] animate-ring-ripple" style={{ animationDelay: "1s" }} />
        </>
      )}
    </motion.button>
  );
}
