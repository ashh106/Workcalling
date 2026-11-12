import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { PointerEvent } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Bug, Mic, Square, Wifi, WifiOff, X } from "lucide-react";
import { ChatInput } from "./ChatInput";
import { MessageContent } from "./MessageContent";
import { Orb } from "./Orb";
import { ResizableSurface } from "./ResizableSurface";
import { normalizeRichMessage } from "./messageAdapter";
import type { AssistantMessage } from "./widgets/types";

type Stage = "voice" | "input" | "chat";

const SAMPLE_WIDGET_JSON = JSON.stringify(
  {
    role: "assistant",
    content: "Here is a local widget payload for testing before the backend contract lands.",
    blocks: [
      {
        kind: "text",
        text: "Here is a local widget payload for **testing rich rendering** before the backend contract lands.",
      },
      {
        kind: "widget",
        widget: {
          type: "bar-chart",
          title: "Sample revenue",
          data: [
            { name: "Jan", value: 65 },
            { name: "Feb", value: 82 },
            { name: "Mar", value: 57 },
            { name: "Apr", value: 73 },
          ],
        },
      },
    ],
    followUps: ["Show a form widget", "Explain these values"],
  },
  null,
  2,
);

export function Assistant({
  messages,
  status,
  hint,
  isConnected,
  isRecording,
  thinking,
  onSend,
  onMic,
  onReset,
  onInjectRichMessage,
  onStopAudio,
}: {
  messages: AssistantMessage[];
  status: string;
  hint: string;
  isConnected: boolean;
  isRecording: boolean;
  thinking: boolean;
  onSend: (text: string) => void;
  onMic: () => void;
  onReset: () => void;
  onInjectRichMessage: (message: AssistantMessage) => void;
  onStopAudio: () => void;
}) {
  const [stage, setStage] = useState<Stage>("input");
  const [devOpen, setDevOpen] = useState(false);
  const [jsonInput, setJsonInput] = useState(SAMPLE_WIDGET_JSON);
  const [jsonError, setJsonError] = useState("");
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const dragStart = useRef<{ x: number; y: number; left: number; top: number } | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const connectionText = useMemo(() => (isConnected ? "Connected" : "Offline"), [isConnected]);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, thinking, hint, stage]);

  const send = useCallback(
    (text: string) => {
      setStage("chat");
      onSend(text);
    },
    [onSend],
  );

  const startVoice = () => {
    setStage("voice");
    if (!isRecording) onMic();
  };

  const closeVoice = () => {
    if (isRecording) onMic();
    setStage(messages.length > 0 ? "chat" : "input");
  };

  const stopVoice = () => {
    if (isRecording) onMic();
    setStage("chat");
  };

  const reset = () => {
    setStage("input");
    setDevOpen(false);
    setPosition({ x: 0, y: 0 });
    onReset();
  };

  const importRichJson = () => {
    setJsonError("");
    try {
      const parsed: unknown = JSON.parse(jsonInput);
      const rich = normalizeRichMessage(parsed);
      if (!rich) {
        setJsonError("JSON must contain role and either content, blocks, or widgets.");
        return;
      }
      onInjectRichMessage(rich);
      setStage("chat");
      setDevOpen(false);
    } catch (error) {
      setJsonError(error instanceof Error ? error.message : "Invalid JSON.");
    }
  };

  const onDragDown = useCallback(
    (event: PointerEvent<HTMLElement>) => {
      const target = event.target as HTMLElement;
      if (target.closest("button, textarea, input, [data-no-drag]")) return;
      event.currentTarget.setPointerCapture(event.pointerId);
      dragStart.current = {
        x: event.clientX,
        y: event.clientY,
        left: position.x,
        top: position.y,
      };
    },
    [position],
  );

  const onDragMove = useCallback((event: PointerEvent<HTMLElement>) => {
    if (!dragStart.current) return;
    const nextX = dragStart.current.left + event.clientX - dragStart.current.x;
    const nextY = dragStart.current.top + event.clientY - dragStart.current.y;
    setPosition({
      x: Math.max(-220, Math.min(220, nextX)),
      y: Math.max(-180, Math.min(180, nextY)),
    });
  }, []);

  const onDragUp = useCallback((event: PointerEvent<HTMLElement>) => {
    (event.target as HTMLElement).releasePointerCapture(event.pointerId);
    dragStart.current = null;
  }, []);

  return (
    <div className="fixed flex flex-col items-center pointer-events-none select-none" style={{ top: 0, left: 0, right: 0, bottom: 0, paddingTop: "24px" }}>
      <div className="pointer-events-auto flex flex-col items-center">
        <AnimatePresence mode="wait">
          {stage === "voice" && (
            <motion.div
              key="voice"
              initial={{ opacity: 0, scale: 0.96, y: -8 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.96, y: -8 }}
              transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
              className="surface-glass rounded-2xl p-10 flex flex-col items-center gap-6 w-[420px] max-w-[92vw]"
            >
              <div onClick={stopVoice} className="cursor-pointer">
                <Orb size={120} mode="voice" />
              </div>
              <div className="text-sm text-[hsl(var(--foreground)/0.6)]">
                {isRecording ? "Listening... speak now" : status}
              </div>
              <div className="flex gap-3">
                <button
                  onClick={closeVoice}
                  className="size-11 rounded-full glass-subtle flex items-center justify-center hover:bg-[hsl(var(--surface-muted)/0.6)] transition-colors"
                >
                  <X size={16} />
                </button>
                <button
                  onClick={stopVoice}
                  className="size-11 rounded-full orb-gradient flex items-center justify-center"
                >
                  <Mic size={16} className="text-primary-foreground" />
                </button>
              </div>
            </motion.div>
          )}

          {stage === "input" && (
            <motion.div
              key="input"
              initial={{ opacity: 0, scale: 0.97, y: -6 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.97, y: -6 }}
              transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="w-[580px] max-w-[92vw]"
            >
              <ChatInput
                onSend={send}
                onMic={startVoice}
                autoFocus
                disabled={!isConnected}
                placeholder="Type a message or use voice..."
              />
            </motion.div>
          )}

          {stage === "chat" && (
            <motion.div
              key="chat"
              initial={{ opacity: 0, scale: 0.97, y: -6 }}
              animate={{ opacity: 1, scale: 1, x: position.x, y: position.y }}
              exit={{ opacity: 0, scale: 0.97, y: -6 }}
              transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
              className="flex flex-col items-center gap-2"
            >
              <ResizableSurface initial={{ w: 680, h: 440 }}>
                <header
                  onPointerDown={onDragDown}
                  onPointerMove={onDragMove}
                  onPointerUp={onDragUp}
                  className="flex items-center justify-between px-4 py-2.5 border-b border-[hsl(var(--glass-border))] cursor-move select-none"
                >
                  <div className="flex items-center gap-3">
                    <div className="size-2.5 rounded-full orb-gradient animate-glow-pulse" />
                    <div>
                      <div className="text-sm font-medium text-[hsl(var(--surface-foreground))]">Workmind</div>
                      <div className="text-[10px] uppercase tracking-wider text-[hsl(var(--foreground)/0.4)]">
                        {hint || status}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2" data-no-drag>
                    {status === "Speaking" && (
                      <button
                        onClick={onStopAudio}
                        className="flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors"
                      >
                        <Square size={10} className="fill-current" />
                        Stop Audio
                      </button>
                    )}
                    <div className="flex items-center gap-1.5 rounded-full glass-subtle px-2.5 py-1 text-[11px] text-[hsl(var(--foreground)/0.7)]">
                      {isConnected ? <Wifi size={12} className="text-green-400" /> : <WifiOff size={12} className="text-red-400" />}
                      {connectionText}
                    </div>
                    <button
                      onClick={() => setDevOpen((open) => !open)}
                      className="size-7 rounded-full hover:bg-[hsl(var(--surface-muted)/0.5)] flex items-center justify-center transition-colors"
                      aria-label="Import rich JSON"
                    >
                      <Bug size={14} className="text-[hsl(var(--foreground)/0.5)]" />
                    </button>
                    <button
                      onClick={reset}
                      className="size-7 rounded-full hover:bg-[hsl(var(--surface-muted)/0.5)] flex items-center justify-center transition-colors"
                      aria-label="Close"
                    >
                      <X size={14} className="text-[hsl(var(--foreground)/0.5)]" />
                    </button>
                  </div>
                </header>

                {devOpen && (
                  <div className="border-b border-[hsl(var(--glass-border))] bg-[hsl(var(--surface-input)/0.6)] p-3 space-y-2" data-no-drag>
                    <textarea
                      value={jsonInput}
                      onChange={(event) => setJsonInput(event.target.value)}
                      className="w-full h-28 rounded-xl glass-input p-3 text-xs font-mono text-[hsl(var(--foreground)/0.85)] outline-none resize-none"
                      spellCheck={false}
                    />
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-xs text-destructive min-h-4">{jsonError}</div>
                      <button
                        onClick={importRichJson}
                        className="rounded-full orb-gradient px-4 py-1.5 text-xs text-primary-foreground hover:brightness-110 transition"
                      >
                        Inject rich data
                      </button>
                    </div>
                  </div>
                )}

                <div
                  ref={scrollRef}
                  className="overflow-y-auto px-5 py-4 space-y-5 custom-scrollbar"
                  style={{ height: devOpen ? "calc(100% - 214px)" : "calc(100% - 57px)" }}
                >
                  {messages.map((message) => <MessageContent key={message.id} message={message} onWidgetSubmit={send} />)}
                  {thinking && (
                    <div className="flex gap-1.5 items-center py-2">
                      <span className="size-2 rounded-full bg-[hsl(var(--primary-glow))] animate-thinking-dot" style={{ animationDelay: "0ms" }} />
                      <span className="size-2 rounded-full bg-[hsl(var(--primary-glow))] animate-thinking-dot" style={{ animationDelay: "160ms" }} />
                      <span className="size-2 rounded-full bg-[hsl(var(--primary-glow))] animate-thinking-dot" style={{ animationDelay: "320ms" }} />
                    </div>
                  )}
                  {!thinking && messages.length > 0 && messages[messages.length - 1].role === "assistant" && messages[messages.length - 1].followUps && (
                    <div className="flex flex-wrap gap-2 pt-2">
                      {messages[messages.length - 1].followUps?.map((followUp) => (
                        <button
                          key={followUp}
                          onClick={() => send(followUp)}
                          className="text-xs px-3 py-1.5 rounded-full glass-subtle hover:bg-[hsl(var(--surface-muted)/0.5)] text-[hsl(var(--foreground)/0.7)] hover:text-[hsl(var(--foreground)/0.9)] transition-all duration-200"
                        >
                          {followUp}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </ResizableSurface>
              <div className="w-[680px] max-w-[92vw]">
                <ChatInput onSend={send} onMic={startVoice} disabled={!isConnected} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
