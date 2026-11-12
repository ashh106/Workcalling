import type { FC } from "react";
import * as W from "./Charts";
import * as S from "./StructuredWidgets";
import * as T from "./ToolWidgets";
import type { Widget } from "./types";

const registry: Record<string, FC<any>> = {
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
  "plan": T.PlanW,
  "progress-tracker": T.ProgressTrackerW,
  "option-list": T.OptionListW,
  "parameter-slider": T.ParameterSliderW,
  "preferences-panel": T.PreferencesPanelW,
  "question-flow": T.QuestionFlowW,
  "citation": T.CitationW,
  "item-carousel": T.ItemCarouselW,
  "link-preview": T.LinkPreviewW,
  "stats-display": T.StatsDisplayW,
  "terminal": T.TerminalW,
  "weather-widget": T.WeatherWidgetW,
  "chart": T.ChartW,
  "code-block": T.CodeBlockW,
  "code-diff": T.CodeDiffW,
  "data-table": T.DataTableW,
  "message-draft": T.MessageDraftW,
  "instagram-post": (props: any) => <T.SocialPostW {...props} platform="Instagram" />,
  "linkedin-post": (props: any) => <T.SocialPostW {...props} platform="LinkedIn" />,
  "x-post": (props: any) => <T.SocialPostW {...props} platform="X" />,
  "approval-card": T.ApprovalCardW,
  "order-summary": T.OrderSummaryW,
  "audio": (props: any) => <T.MediaW {...props} type="audio" />,
  "image": (props: any) => <T.MediaW {...props} type="image" />,
  "image-gallery": T.ImageGalleryW,
  "video": (props: any) => <T.MediaW {...props} type="video" />,
  "geo-map": T.GeoMapW,
};

export function WidgetRenderer({ widget, onSubmit }: { widget: Widget; onSubmit?: (text: string) => void }) {
  const Cmp = registry[widget.type];
  if (!Cmp) return <div className="text-xs opacity-60">Unknown widget: {widget.type}</div>;
  return <Cmp title={widget.title} data={widget.data} onSubmit={onSubmit} />;
}
