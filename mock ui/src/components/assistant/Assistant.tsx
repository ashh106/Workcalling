import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, Square } from "lucide-react";
import { Orb } from "./Orb";
import { ChatInput } from "./ChatInput";
import { MessageContent } from "./MessageContent";
import { ResizableSurface } from "./ResizableSurface";
import type { AssistantMessage } from "./widgets/types";
import { generateMockReply } from "./mockResponses";

type Stage = "voice" | "input" | "chat";

export function Assistant() {
  const [stage, setStage] = useState<Stage>("input");
  const [messages, setMessages] = useState<AssistantMessage[]>([]);
  const [thinking, setThinking] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, thinking, stage]);

  const send = (text: string) => {
    const userMsg: AssistantMessage = { id: crypto.randomUUID(), role: "user", blocks: [{ kind: "text", text }] };
    setMessages((m) => [...m, userMsg]);
    setStage("chat");
    setThinking(true);
    window.setTimeout(() => {
      setMessages((m) => [...m, generateMockReply(text)]);
      setThinking(false);
    }, 700);
  };

  const finishVoice = () => {
    send("Visualize my activity heatmap and weekly trend");
  };

  const reset = () => {
    setStage("input");
    setMessages([]);
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center pointer-events-none">
      <div className="pointer-events-auto">
        <AnimatePresence mode="wait">
          {stage === "voice" && (
            <motion.div key="voice" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
              className="surface-glass rounded-[2rem] p-10 flex flex-col items-center gap-6 w-[420px]">
              <Orb size={120} mode="voice" />
              <div className="text-sm opacity-70">Listening… speak now</div>
              <div className="flex gap-3">
                <button onClick={() => setStage(messages.length > 0 ? "chat" : "input")} className="size-11 rounded-full bg-[hsl(var(--surface-muted))] flex items-center justify-center hover:bg-[hsl(var(--surface-muted))]/70">
                  <X size={16} />
                </button>
                <button onClick={finishVoice} className="size-11 rounded-full orb-gradient flex items-center justify-center">
                  <Square size={14} className="text-primary-foreground fill-current" />
                </button>
              </div>
            </motion.div>
          )}

          {stage === "input" && (
            <motion.div key="input" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="w-[560px] max-w-[92vw]">
              <div className="relative">
                <ChatInput onSend={send} onMic={() => setStage("voice")} autoFocus placeholder="Type a message or use voice..." />
              </div>
            </motion.div>
          )}

          {stage === "chat" && (
            <motion.div key="chat" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-3">
              <ResizableSurface initial={{ w: 720, h: 480 }}>
                <div className="flex items-center justify-between px-5 py-3 border-b border-[hsl(var(--surface-border))]">
                  <div className="flex items-center gap-2">
                    <div className="size-2.5 rounded-full orb-gradient" />
                    <div className="text-sm font-medium">Assistant</div>
                  </div>
                  <button onClick={reset} className="size-7 rounded-full hover:bg-[hsl(var(--surface-muted))] flex items-center justify-center" aria-label="Close">
                    <X size={14} />
                  </button>
                </div>
                <div ref={scrollRef} className="overflow-y-auto px-5 py-4 space-y-5" style={{ height: "calc(100% - 53px)" }}>
                  {messages.map((m) => <MessageContent key={m.id} message={m} />)}
                  {thinking && (
                    <div className="flex gap-1.5 items-center">
                      <span className="size-1.5 rounded-full bg-[hsl(var(--primary-glow))] animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="size-1.5 rounded-full bg-[hsl(var(--primary-glow))] animate-bounce" style={{ animationDelay: "120ms" }} />
                      <span className="size-1.5 rounded-full bg-[hsl(var(--primary-glow))] animate-bounce" style={{ animationDelay: "240ms" }} />
                    </div>
                  )}
                  {!thinking && messages.length > 0 && messages[messages.length - 1].role === "assistant" && messages[messages.length - 1].followUps && (
                    <div className="flex flex-wrap gap-2 pt-1">
                      {messages[messages.length - 1].followUps!.map((f) => (
                        <button key={f} onClick={() => send(f)} className="text-xs px-3 py-1.5 rounded-full bg-[hsl(var(--surface-muted))] hover:bg-[hsl(var(--surface-input))] transition">
                          {f}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </ResizableSurface>
              <div className="w-[640px] max-w-[92vw]">
                <ChatInput onSend={send} onMic={() => setStage("voice")} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
