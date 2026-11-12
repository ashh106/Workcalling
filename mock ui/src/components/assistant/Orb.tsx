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
      whileHover={{ scale: 1.06 }}
      whileTap={{ scale: 0.94 }}
      className={cn(
        "relative rounded-full orb-gradient cursor-pointer outline-none focus-visible:ring-4 focus-visible:ring-primary/40",
        mode === "voice" && "animate-orb-pulse"
      )}
      style={{ width: size, height: size }}
      aria-label="Assistant orb"
    >
      <span className={cn("absolute inset-0 rounded-full", mode === "idle" && "animate-orb-breathe orb-gradient")} />
      {mode === "voice" && (
        <>
          <span className="absolute inset-0 rounded-full border-2 border-[hsl(var(--primary-glow))] animate-ring-ripple" />
          <span className="absolute inset-0 rounded-full border-2 border-[hsl(var(--primary-glow))] animate-ring-ripple" style={{ animationDelay: "0.5s" }} />
        </>
      )}
    </motion.button>
  );
}
