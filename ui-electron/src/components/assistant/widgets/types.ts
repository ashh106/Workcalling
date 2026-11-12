export type WidgetType =
  | "bar-chart" | "line-chart" | "donut-chart" | "radar"
  | "scatter" | "heatmap" | "funnel" | "waterfall"
  | "treemap" | "sankey" | "sparkline" | "network"
  | "tabs" | "form"
  | "plan" | "progress-tracker"
  | "option-list" | "parameter-slider" | "preferences-panel" | "question-flow"
  | "citation" | "item-carousel" | "link-preview" | "stats-display"
  | "terminal" | "weather-widget"
  | "chart" | "code-block" | "code-diff" | "data-table" | "message-draft"
  | "instagram-post" | "linkedin-post" | "x-post"
  | "approval-card" | "order-summary"
  | "audio" | "image" | "image-gallery" | "video"
  | "geo-map";

export interface Widget {
  type: WidgetType;
  title?: string;
  data: unknown;
}

export interface AssistantBlock {
  kind: "text" | "widget";
  text?: string;
  widget?: Widget;
}

export interface AssistantMessage {
  id: string;
  role: "user" | "assistant";
  blocks: AssistantBlock[];
  followUps?: string[];
}
