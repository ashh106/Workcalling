import { useEffect, useMemo, useRef, useState } from "react";
import { Assistant } from "@/components/assistant/Assistant";
import { adaptChatMessage, richMessageToChatMessage } from "@/components/assistant/messageAdapter";
import type { AssistantMessage } from "@/components/assistant/widgets/types";
import { ChatService } from "@/services/ChatService";
import type { ChatMessage } from "@/services/ChatService";
import { VoiceService } from "@/services/VoiceService";
import "./App.css";

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [status, setStatus] = useState("Idle");
  const [hint, setHint] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [thinking, setThinking] = useState(false);

  const chatService = useRef<ChatService | null>(null);
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const messagesRef = useRef<ChatMessage[]>([]);
  const currentAudio = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  const stopAudio = () => {
    if (currentAudio.current) {
      currentAudio.current.pause();
      currentAudio.current.currentTime = 0;
      currentAudio.current = null;
      setStatus(isConnected ? "Idle" : "Offline");
    }
  };

  useEffect(() => {
    chatService.current = new ChatService(
      (msg) => {
        if (msg.type === "hint") {
          setHint(msg.content || "");
          setStatus("Processing");
          setThinking(true);
          return;
        }

        if (msg.type === "response") {
          const newMessages = msg.messages || [];
          setMessages((prev) => [...prev, ...newMessages]);
          setThinking(false);
          setHint("");

          const lastAssistant = [...newMessages].reverse().find((message) => message.role === "assistant");
          if (lastAssistant?.content) {
            setStatus("Speaking");
            stopAudio(); // Stop any currently playing audio
            VoiceService.textToSpeech(lastAssistant.content)
              .then((audio) => {
                if (!audio) {
                  setStatus("Idle");
                  return;
                }

                currentAudio.current = audio;
                audio.play().catch((error: unknown) => {
                  console.error("Audio playback failed:", error);
                  setStatus("Idle");
                  currentAudio.current = null;
                });
                audio.onended = () => {
                  setStatus("Idle");
                  currentAudio.current = null;
                };
              })
              .catch((error: unknown) => {
                console.error("TTS service failed:", error);
                setStatus("Idle");
              });
          } else {
            setStatus("Idle");
          }
        }
      },
      (connected) => {
        setIsConnected(connected);
        setStatus(connected ? "Idle" : "Offline");
        if (!connected) {
          setHint("");
          setThinking(false);
          stopAudio();
        }
      },
    );

    chatService.current.connect();

    return () => {
      chatService.current?.disconnect();
      stopAudio();
    };
  }, []);

  const sendText = (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || !isConnected) return;

    stopAudio();
    const userMessage: ChatMessage = { role: "user", content: trimmed };
    const nextMessages = [...messagesRef.current, userMessage];
    setMessages(nextMessages);
    messagesRef.current = nextMessages;
    chatService.current?.sendMessage(nextMessages);
    setStatus("Thinking...");
    setHint("");
    setThinking(true);
  };

  const toggleRecording = async () => {
    try {
      if (isRecording) {
        mediaRecorder.current?.stop();
        setIsRecording(false);
        setStatus("Processing Voice...");
        return;
      }

      stopAudio();
      setStatus("Starting Mic...");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: "audio/wav" });
        
        stream.getTracks().forEach((track) => track.stop());

        if (audioBlob.size === 0) {
          setStatus("Idle");
          return;
        }

        const text = await VoiceService.speechToText(audioBlob);

        if (text) {
          setStatus("Ready");
          sendText(text);
        } else {
          setStatus("STT Failed");
        }
      };

      mediaRecorder.current.start();
      setIsRecording(true);
      setStatus("Listening...");
    } catch (error) {
      console.error("Microphone error:", error);
      setIsRecording(false);
      setStatus("Mic Error");
    }
  };

  const reset = () => {
    stopAudio();
    setMessages([]);
    messagesRef.current = [];
    setHint("");
    setThinking(false);
    setStatus(isConnected ? "Idle" : "Offline");
  };

  const injectRichMessage = (message: AssistantMessage) => {
    stopAudio();
    const chatMessage = richMessageToChatMessage(message);
    setMessages((prev) => {
      const next = [...prev, chatMessage];
      messagesRef.current = next;
      return next;
    });
  };

  const assistantMessages = useMemo(
    () => messages.map((message, index) => adaptChatMessage(message, index)),
    [messages],
  );

  return (
    <main className="relative overflow-hidden" style={{ minHeight: "100vh", background: "transparent" }}>
      <Assistant
        messages={assistantMessages}
        status={status}
        hint={hint}
        isConnected={isConnected}
        isRecording={isRecording}
        thinking={thinking}
        onSend={sendText}
        onMic={toggleRecording}
        onReset={reset}
        onInjectRichMessage={injectRichMessage}
        onStopAudio={stopAudio}
      />
    </main>
  );
}

export default App;
