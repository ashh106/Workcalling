import { Mic, ArrowUp } from "lucide-react";
import { useRef, useState, KeyboardEvent } from "react";
import { cn } from "@/lib/utils";

export function ChatInput({
  onSend,
  onMic,
  placeholder = "Ask anything you want ...",
  className,
  autoFocus,
}: {
  onSend: (text: string) => void;
  onMic?: () => void;
  placeholder?: string;
  className?: string;
  autoFocus?: boolean;
}) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  const send = () => {
    const v = value.trim();
    if (!v) return;
    onSend(v);
    setValue("");
  };

  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className={cn("flex items-end gap-2 rounded-full bg-[hsl(var(--surface-input))] border border-[hsl(var(--surface-border))] px-5 py-2.5", className)}>
      <textarea
        ref={ref}
        autoFocus={autoFocus}
        rows={1}
        value={value}
        onChange={(e) => {
          setValue(e.target.value);
          const el = e.target as HTMLTextAreaElement;
          el.style.height = "auto";
          el.style.height = Math.min(el.scrollHeight, 120) + "px";
        }}
        onKeyDown={onKey}
        placeholder={placeholder}
        className="flex-1 resize-none bg-transparent outline-none text-[hsl(var(--surface-foreground))] placeholder:text-[hsl(var(--surface-foreground))]/40 text-sm leading-6 max-h-[120px]"
      />
      <button
        onClick={onMic}
        className="size-8 rounded-full orb-gradient flex items-center justify-center shrink-0 hover:brightness-110 transition"
        aria-label="Voice"
      >
        <Mic size={14} className="text-primary-foreground" />
      </button>
      <button
        onClick={send}
        disabled={!value.trim()}
        className="size-8 rounded-full orb-gradient flex items-center justify-center shrink-0 hover:brightness-110 transition disabled:opacity-40 disabled:cursor-not-allowed"
        aria-label="Send"
      >
        <ArrowUp size={14} className="text-primary-foreground" />
      </button>
    </div>
  );
}
