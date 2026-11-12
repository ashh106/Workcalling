import type { ChatMessage } from "@/services/ChatService";
import type { AssistantBlock, AssistantMessage, Widget, WidgetType } from "./widgets/types";

const WIDGET_TYPES = new Set<WidgetType>([
  "bar-chart",
  "line-chart",
  "donut-chart",
  "radar",
  "scatter",
  "heatmap",
  "funnel",
  "waterfall",
  "treemap",
  "sankey",
  "sparkline",
  "network",
  "tabs",
  "form",
  "plan",
  "progress-tracker",
  "option-list",
  "parameter-slider",
  "preferences-panel",
  "question-flow",
  "citation",
  "item-carousel",
  "link-preview",
  "stats-display",
  "terminal",
  "weather-widget",
  "chart",
  "code-block",
  "code-diff",
  "data-table",
  "message-draft",
  "instagram-post",
  "linkedin-post",
  "x-post",
  "approval-card",
  "order-summary",
  "audio",
  "image",
  "image-gallery",
  "video",
  "geo-map",
]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isWidgetType(value: unknown): value is WidgetType {
  return typeof value === "string" && WIDGET_TYPES.has(value as WidgetType);
}

function normalizeWidget(value: unknown): Widget | null {
  if (!isRecord(value) || !isWidgetType(value.type)) return null;
  return {
    type: value.type,
    title: typeof value.title === "string" ? value.title : undefined,
    data: value.data,
  };
}

function normalizeBlock(value: unknown): AssistantBlock | null {
  if (!isRecord(value) || typeof value.kind !== "string") return null;

  if (value.kind === "text" && typeof value.text === "string") {
    return { kind: "text", text: value.text };
  }

  if (value.kind === "widget") {
    const widget = normalizeWidget(value.widget);
    if (widget) return { kind: "widget", widget };
  }

  return null;
}

function parseJsonObject(value: string): Record<string, unknown> | null {
  const trimmed = value.trim();
  if (!trimmed.startsWith("{")) return null;

  try {
    const parsed: unknown = JSON.parse(trimmed);
    return isRecord(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

function textFromUnknown(value: unknown): string {
  if (typeof value === "string") return value;
  if (value === undefined || value === null) return "";
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export function normalizeRichMessage(raw: unknown, fallbackId: string = crypto.randomUUID()): AssistantMessage | null {
  if (!isRecord(raw)) return null;

  const role = raw.role === "user" ? "user" : raw.role === "assistant" ? "assistant" : null;
  if (!role) return null;

  const blocks: AssistantBlock[] = [];
  if (Array.isArray(raw.blocks)) {
    for (const block of raw.blocks) {
      const normalized = normalizeBlock(block);
      if (normalized) blocks.push(normalized);
    }
  }

  if (blocks.length === 0 && Array.isArray(raw.widgets)) {
    const content = textFromUnknown(raw.content).trim();
    if (content) blocks.push({ kind: "text", text: content });
    for (const candidate of raw.widgets) {
      const widget = normalizeWidget(candidate);
      if (widget) blocks.push({ kind: "widget", widget });
    }
  }

  if (blocks.length === 0) {
    blocks.push({ kind: "text", text: textFromUnknown(raw.content) });
  }

  const followUps = Array.isArray(raw.followUps)
    ? raw.followUps.filter((item): item is string => typeof item === "string")
    : undefined;

  return {
    id: typeof raw.id === "string" ? raw.id : fallbackId,
    role,
    blocks,
    followUps,
  };
}

export function adaptChatMessage(message: ChatMessage, index: number): AssistantMessage {
  const parsed = typeof message.content === "string" ? parseJsonObject(message.content) : null;
  const rich = normalizeRichMessage(parsed ?? message, `message-${index}-${message.role}`);
  if (rich) return rich;

  return {
    id: `message-${index}-${message.role}`,
    role: message.role === "user" ? "user" : "assistant",
    blocks: [{ kind: "text", text: textFromUnknown(message.content) }],
  };
}

export function richMessageToChatMessage(message: AssistantMessage): ChatMessage {
  const text = message.blocks
    .filter((block) => block.kind === "text" && block.text)
    .map((block) => block.text)
    .join("\n\n");

  return {
    role: message.role,
    content: text,
    blocks: message.blocks,
    followUps: message.followUps,
  };
}
