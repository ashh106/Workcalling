export type WidgetType =
  | "bar-chart" | "line-chart" | "donut-chart" | "radar"
  | "scatter" | "heatmap" | "funnel" | "waterfall"
  | "treemap" | "sankey" | "sparkline" | "network"
  | "tabs" | "form";

export interface Widget {
  type: WidgetType;
  title?: string;
  data: any;
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
