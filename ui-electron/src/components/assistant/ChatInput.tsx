import { Mic, ArrowUp } from "lucide-react";
import { useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import { cn } from "@/lib/utils";

export function ChatInput({
  onSend,
  onMic,
  placeholder = "Ask anything you want ...",
  className,
  autoFocus,
  disabled = false,
}: {
  onSend: (text: string) => void;
  onMic?: () => void;
  placeholder?: string;
  className?: string;
  autoFocus?: boolean;
  disabled?: boolean;
}) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  const send = () => {
    const v = value.trim();
    if (!v || disabled) return;
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
    <div
      className={cn(
        "flex items-end gap-2 rounded-2xl glass-input px-5 py-3",
        disabled && "opacity-50",
        className,
      )}
    >
      <textarea
        ref={ref}
        autoFocus={autoFocus}
        disabled={disabled}
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
        className="flex-1 resize-none bg-transparent outline-none text-[hsl(var(--foreground)/0.9)] placeholder:text-[hsl(var(--foreground)/0.3)] text-sm leading-6 max-h-[120px]"
      />
      <button
        onClick={onMic}
        disabled={disabled}
        className="size-8 rounded-full orb-gradient flex items-center justify-center shrink-0 hover:brightness-110 hover:scale-105 transition-all duration-200"
        aria-label="Voice"
      >
        <Mic size={14} className="text-primary-foreground" />
      </button>
      <button
        onClick={send}
        disabled={!value.trim() || disabled}
        className="size-8 rounded-full orb-gradient flex items-center justify-center shrink-0 hover:brightness-110 hover:scale-105 transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed disabled:scale-100"
        aria-label="Send"
      >
        <ArrowUp size={14} className="text-primary-foreground" />
      </button>
    </div>
  );
}
