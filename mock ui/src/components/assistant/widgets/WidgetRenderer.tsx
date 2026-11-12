import * as W from "./Charts";
import * as S from "./StructuredWidgets";
import type { Widget } from "./types";

const registry: Record<string, React.FC<any>> = {
  "bar-chart": W.BarChartW,
  "line-chart": W.LineChartW,
  "donut-chart": W.DonutChartW,
  "radar": W.RadarW,
  "scatter": W.ScatterW,
  "heatmap": W.HeatmapW,
  "funnel": W.FunnelW,
  "waterfall": W.WaterfallW,
  "treemap": W.TreemapW,
  "sparkline": W.SparklineW,
  "sankey": W.SankeyW,
  "network": W.NetworkW,
  "tabs": S.TabsW,
  "form": S.FormW,
};

export function WidgetRenderer({ widget }: { widget: Widget }) {
  const Cmp = registry[widget.type];
  if (!Cmp) return <div className="text-xs opacity-60">Unknown widget: {widget.type}</div>;
  return <Cmp title={widget.title} data={widget.data} />;
}
