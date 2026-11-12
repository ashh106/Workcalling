import type { AssistantMessage } from "./widgets/types";

const samples = {
  bar: [
    { name: "Jan", value: 65 }, { name: "Feb", value: 82 }, { name: "Mar", value: 57 },
    { name: "Apr", value: 73 }, { name: "May", value: 64 }, { name: "Jun", value: 60 },
    { name: "Jul", value: 88 }, { name: "Aug", value: 71 },
  ],
  line: [
    { name: "Jan", value: 30 }, { name: "Feb", value: 45 }, { name: "Mar", value: 38 },
    { name: "Apr", value: 60 }, { name: "May", value: 64 }, { name: "Jun", value: 70 },
    { name: "Jul", value: 84 }, { name: "Aug", value: 92 },
  ],
  donut: [
    { name: "Active", value: 4200000 },
    { name: "Idle", value: 1800000 },
    { name: "Churned", value: 600000 },
  ],
  radar: [
    { name: "Power", value: 80 }, { name: "Range", value: 65 },
    { name: "Safety", value: 92 }, { name: "Cost", value: 70 }, { name: "Comfort", value: 78 },
  ],
  scatter: Array.from({ length: 18 }, () => ({ x: Math.random() * 100, y: Math.random() * 100, z: Math.random() * 600 })),
  heatmap: {
    rows: ["Mon", "Tue", "Wed", "Thu", "Fri"],
    cols: ["8am", "10am", "12pm", "2pm", "4pm", "6pm", "8pm"],
    values: Array.from({ length: 5 }, () => Array.from({ length: 7 }, () => Math.round(Math.random() * 100))),
  },
  funnel: [
    { name: "Visitors", value: 12400 }, { name: "Leads", value: 8200 },
    { name: "Trials", value: 3100 }, { name: "Customers", value: 1040 },
  ],
  waterfall: [
    { name: "Start", value: 100, type: "start" },
    { name: "Q1", value: 30, type: "pos" },
    { name: "Q2", value: 20, type: "pos" },
    { name: "Costs", value: -25, type: "neg" },
    { name: "Q3", value: 15, type: "pos" },
    { name: "Total", value: 140, type: "total" },
  ],
  treemap: [
    { name: "Engineering", value: 45 }, { name: "Sales", value: 22 },
    { name: "Marketing", value: 12 }, { name: "Ops", value: 15 }, { name: "HR", value: 7 },
  ],
  sparkline: Array.from({ length: 14 }, (_, i) => ({ name: `${i}`, value: 40 + i * 3 + Math.random() * 10 })),
  sankey: [
    { name: "Budget", value: 4200 }, { name: "Actual", value: 3800 }, { name: "Forecast", value: 3100 },
  ],
  network: {
    nodes: [
      { id: "A", x: 20, y: 20 }, { id: "B", x: 80, y: 25 },
      { id: "C", x: 50, y: 50, main: true }, { id: "D", x: 25, y: 80 }, { id: "E", x: 78, y: 78 },
    ],
    edges: [["A", "C"], ["B", "C"], ["D", "C"], ["E", "C"]] as [string, string][],
  },
  tabs: {
    tabs: [
      {
        id: "overview", label: "Overview",
        kpis: [
          { label: "Revenue", value: "$48.2k", delta: "+12.4%" },
          { label: "Users", value: "2,318", delta: "+4.1%" },
          { label: "Churn", value: "1.8%", delta: "-0.3%" },
        ],
        text: "Performance is trending upward across all key metrics this quarter.",
      },
      {
        id: "analytics", label: "Analytics",
        rows: [
          { label: "Sessions", value: "12,402" },
          { label: "Avg. duration", value: "3m 42s" },
          { label: "Bounce rate", value: "28%" },
          { label: "Conversion", value: "4.6%" },
        ],
      },
      {
        id: "settings", label: "Settings",
        text: "Adjust thresholds, integrations, and notification preferences for this workspace.",
      },
    ],
  },
  form: {
    fields: [
      { name: "name", label: "Name", type: "text", placeholder: "John Doe", required: true },
      { name: "email", label: "Email", type: "email", placeholder: "john@acme.com", required: true },
      { name: "role", label: "Role", type: "select", placeholder: "Choose a role", options: [
        { value: "designer", label: "Designer" },
        { value: "developer", label: "Developer" },
        { value: "pm", label: "Product manager" },
      ]},
      { name: "plan", label: "Plan", type: "radio", options: [
        { value: "free", label: "Free" }, { value: "pro", label: "Pro" }, { value: "team", label: "Team" },
      ]},
      { name: "interests", label: "Interests", type: "checkbox", options: [
        { value: "ai", label: "AI" }, { value: "data", label: "Data" }, { value: "design", label: "Design" },
      ]},
      { name: "notify", label: "Email notifications", type: "switch" },
      { name: "budget", label: "Budget ($)", type: "slider", min: 0, max: 1000, step: 50 },
      { name: "notes", label: "Notes", type: "textarea", placeholder: "Anything else?" },
    ],
    submitLabel: "Submit",
    cancelLabel: "Cancel",
  },
};

const widgetTypes = [
  "bar-chart", "line-chart", "donut-chart", "radar", "scatter", "heatmap",
  "funnel", "waterfall", "treemap", "sparkline", "sankey", "network",
  "tabs", "form",
] as const;

const dataMap: Record<string, any> = {
  "bar-chart": samples.bar, "line-chart": samples.line, "donut-chart": samples.donut,
  "radar": samples.radar, "scatter": samples.scatter, "heatmap": samples.heatmap,
  "funnel": samples.funnel, "waterfall": samples.waterfall, "treemap": samples.treemap,
  "sparkline": samples.sparkline, "sankey": samples.sankey, "network": samples.network,
  "tabs": samples.tabs, "form": samples.form,
};

let counter = 0;
const titleMap: Record<string, string> = {
  "bar-chart": "Monthly revenue", "line-chart": "Growth trend", "donut-chart": "User distribution",
  "radar": "Product attributes", "scatter": "Correlation analysis", "heatmap": "Activity by hour",
  "funnel": "Conversion funnel", "waterfall": "Quarterly delta", "treemap": "Department spend",
  "sparkline": "Trend (14d)", "sankey": "Budget allocation", "network": "Dependency graph",
  "tabs": "Workspace overview", "form": "Quick details",
};

export function generateMockReply(prompt: string): AssistantMessage {
  // Try to detect a widget hint in the prompt
  const lower = prompt.toLowerCase();
  let type = widgetTypes.find((t) => lower.includes(t.replace("-chart", "")) || lower.includes(t));
  if (!type) {
    type = widgetTypes[counter++ % widgetTypes.length];
  }

  return {
    id: crypto.randomUUID(),
    role: "assistant",
    blocks: [
      {
        kind: "text",
        text:
          `Here's what I found for **"${prompt}"**. I've prepared a visualization to help you explore:\n\n` +
          `- Visualizing tool execution with loading states and progress indicators\n` +
          `- Displaying results in rich, formatted layouts\n` +
          `- Enabling user interaction through forms and controls\n` +
          `- Providing error feedback with helpful recovery options`,
      },
      { kind: "widget", widget: { type, title: titleMap[type], data: dataMap[type] } },
    ],
    followUps: ["Show me a different chart", "Explain these numbers", "Export this view"],
  };
}
