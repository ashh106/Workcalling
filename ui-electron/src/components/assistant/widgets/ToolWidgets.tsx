import { useState } from "react";
import type { ReactNode } from "react";
import { Check, ExternalLink, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import * as Charts from "./Charts";

type WidgetSubmit = (text: string) => void;

const Wrap = ({ title, children }: { title?: string; children: ReactNode }) => (
  <div className="rounded-2xl glass-subtle p-4">
    {title && <div className="text-xs font-medium text-[hsl(var(--foreground)/0.6)] mb-3">{title}</div>}
    {children}
  </div>
);

function isRecord(value: unknown): value is Record<string, any> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asArray(value: unknown): any[] {
  return Array.isArray(value) ? value : [];
}

function arrayFromData(data: unknown, keys: string[]): any[] {
  if (Array.isArray(data)) return data;
  if (!isRecord(data)) return [];
  for (const key of keys) {
    if (Array.isArray(data[key])) return data[key];
  }
  return [];
}

function text(value: unknown, fallback = "") {
  if (typeof value === "string") return value;
  if (value === null || value === undefined) return fallback;
  return String(value);
}

function submitWidget(type: string, title: string | undefined, action: string, values: unknown, onSubmit?: WidgetSubmit) {
  if (!onSubmit) return;
  const payload = {
    widgetType: type,
    title,
    action,
    values,
  };
  onSubmit(`Widget submission: ${title || type}\n\n${JSON.stringify(payload, null, 2)}`);
}

function StatusPill({ status }: { status?: string }) {
  const s = status || "pending";
  return (
    <span className="rounded-full border border-[hsl(var(--glass-border))] px-2 py-0.5 text-[10px] uppercase tracking-wide text-[hsl(var(--foreground)/0.6)]">
      {s}
    </span>
  );
}

export function PlanW({ title, data }: any) {
  const steps = arrayFromData(data, ["steps", "items"]);
  return (
    <Wrap title={title}>
      <ol className="space-y-3">
        {steps.map((step, index) => (
          <li key={step.id || index} className="flex gap-3">
            <div className="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full bg-[hsl(var(--surface-muted))] text-xs">
              {index + 1}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-3">
                <div className="text-sm font-medium">{text(step.title || step.label, `Step ${index + 1}`)}</div>
                <StatusPill status={step.status} />
              </div>
              {step.description && <p className="mt-1 text-xs leading-relaxed text-[hsl(var(--foreground)/0.65)]">{step.description}</p>}
            </div>
          </li>
        ))}
      </ol>
    </Wrap>
  );
}

export function ProgressTrackerW({ title, data }: any) {
  const items = arrayFromData(data, ["steps", "items", "tasks"]);
  const completed = items.filter((item) => ["complete", "completed", "done"].includes(text(item.status).toLowerCase())).length;
  const pct = items.length ? Math.round((completed / items.length) * 100) : Number(data?.percent ?? 0);
  return (
    <Wrap title={title}>
      <div className="mb-3 h-2 overflow-hidden rounded-full bg-[hsl(var(--surface-muted))]">
        <div className="h-full rounded-full orb-gradient" style={{ width: `${Math.max(0, Math.min(100, pct))}%` }} />
      </div>
      <div className="space-y-2">
        {items.map((item, index) => (
          <div key={item.id || index} className="flex items-center justify-between gap-3 text-sm">
            <span className="truncate text-[hsl(var(--foreground)/0.8)]">{text(item.title || item.label, `Item ${index + 1}`)}</span>
            <StatusPill status={item.status} />
          </div>
        ))}
      </div>
    </Wrap>
  );
}

export function StatsDisplayW({ title, data }: any) {
  const stats = arrayFromData(data, ["stats", "metrics", "items"]);
  return (
    <Wrap title={title}>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {stats.map((stat, index) => (
          <div key={stat.id || stat.label || index} className="rounded-xl bg-[hsl(var(--surface-muted)/0.45)] p-3">
            <div className="text-[11px] text-[hsl(var(--foreground)/0.55)]">{text(stat.label || stat.name)}</div>
            <div className="mt-1 text-lg font-semibold">{text(stat.value)}</div>
            {stat.delta && <div className="mt-1 text-xs text-[hsl(var(--primary-glow))]">{text(stat.delta)}</div>}
          </div>
        ))}
      </div>
    </Wrap>
  );
}

export function DataTableW({ title, data }: any) {
  const rows = arrayFromData(data, ["rows", "data", "items"]);
  const columns = asArray(data?.columns);
  const inferred = rows[0] && isRecord(rows[0]) ? Object.keys(rows[0]) : [];
  const keys = columns.length ? columns.map((col) => col.key || col.id || col.accessor || col.label).filter(Boolean) : inferred;
  return (
    <Wrap title={title}>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[420px] text-left text-xs">
          <thead className="text-[hsl(var(--foreground)/0.55)]">
            <tr>
              {keys.map((key) => (
                <th key={key} className="border-b border-[hsl(var(--glass-border))] px-2 py-2 font-medium">
                  {text(columns.find((col) => (col.key || col.id || col.accessor || col.label) === key)?.label || key)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={row.id || index}>
                {keys.map((key) => (
                  <td key={key} className="border-b border-[hsl(var(--glass-border))] px-2 py-2 text-[hsl(var(--foreground)/0.75)]">
                    {text(isRecord(row) ? row[key] : row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Wrap>
  );
}

export function OptionListW({ title, data, onSubmit }: any) {
  const options = arrayFromData(data, ["options", "items", "choices"]);
  const multiple = Boolean(data?.multiple);
  const [selected, setSelected] = useState<string[]>([]);
  const toggle = (id: string) => setSelected((prev) => (
    multiple
      ? prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
      : [id]
  ));
  return (
    <Wrap title={title}>
      <div className="space-y-2">
        {options.map((option, index) => {
          const id = text(option.id || option.value || index);
          const active = selected.includes(id);
          return (
            <button
              key={id}
              type="button"
              onClick={() => toggle(id)}
              className={`w-full rounded-xl border px-3 py-2 text-left transition ${active ? "border-[hsl(var(--primary))] bg-[hsl(var(--primary)/0.12)]" : "border-[hsl(var(--glass-border))] bg-transparent"}`}
            >
              <div className="text-sm font-medium">{text(option.label || option.title || id)}</div>
              {option.description && <div className="mt-0.5 text-xs text-[hsl(var(--foreground)/0.6)]">{option.description}</div>}
            </button>
          );
        })}
      </div>
      <Button className="mt-3 w-full" disabled={!selected.length} onClick={() => submitWidget("option-list", title, "confirm", selected, onSubmit)}>
        Submit
      </Button>
    </Wrap>
  );
}

export function ParameterSliderW({ title, data, onSubmit }: any) {
  const sliders = arrayFromData(data, ["sliders", "parameters", "items"]);
  const [values, setValues] = useState<Record<string, number>>(() => Object.fromEntries(
    sliders.map((slider, index) => [text(slider.id || slider.name || index), Number(slider.value ?? slider.default ?? slider.min ?? 0)]),
  ));
  return (
    <Wrap title={title}>
      <div className="space-y-4">
        {sliders.map((slider, index) => {
          const id = text(slider.id || slider.name || index);
          return (
            <div key={id} className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span>{text(slider.label || slider.name || id)}</span>
                <span className="text-[hsl(var(--foreground)/0.6)]">{values[id]}</span>
              </div>
              <Slider
                value={[values[id] ?? 0]}
                min={Number(slider.min ?? 0)}
                max={Number(slider.max ?? 100)}
                step={Number(slider.step ?? 1)}
                onValueChange={(next) => setValues((prev) => ({ ...prev, [id]: next[0] }))}
              />
            </div>
          );
        })}
      </div>
      <Button className="mt-4 w-full" onClick={() => submitWidget("parameter-slider", title, "submit", values, onSubmit)}>
        Submit
      </Button>
    </Wrap>
  );
}

export function PreferencesPanelW({ title, data, onSubmit }: any) {
  const prefs = arrayFromData(data, ["preferences", "settings", "items"]);
  const [values, setValues] = useState<Record<string, any>>(() => Object.fromEntries(
    prefs.map((pref, index) => [text(pref.id || pref.name || index), pref.value ?? pref.default ?? false]),
  ));
  return (
    <Wrap title={title}>
      <div className="space-y-3">
        {prefs.map((pref, index) => {
          const id = text(pref.id || pref.name || index);
          const kind = text(pref.type || pref.kind, "switch");
          return (
            <div key={id} className="flex items-center justify-between gap-3 rounded-xl bg-[hsl(var(--surface-muted)/0.35)] px-3 py-2">
              <div>
                <div className="text-sm">{text(pref.label || pref.name || id)}</div>
                {pref.description && <div className="text-xs text-[hsl(var(--foreground)/0.55)]">{pref.description}</div>}
              </div>
              {kind === "text" ? (
                <Input className="w-36" value={values[id] ?? ""} onChange={(event) => setValues((prev) => ({ ...prev, [id]: event.target.value }))} />
              ) : (
                <Switch checked={Boolean(values[id])} onCheckedChange={(checked) => setValues((prev) => ({ ...prev, [id]: checked }))} />
              )}
            </div>
          );
        })}
      </div>
      <Button className="mt-4 w-full" onClick={() => submitWidget("preferences-panel", title, "submit", values, onSubmit)}>
        Submit
      </Button>
    </Wrap>
  );
}

export function QuestionFlowW({ title, data, onSubmit }: any) {
  const questions = arrayFromData(data, ["questions", "steps", "items"]);
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const current = questions[index];
  const id = current ? text(current.id || current.name || index) : "";
  if (!current) return null;
  const last = index >= questions.length - 1;
  return (
    <Wrap title={title}>
      <div className="text-xs text-[hsl(var(--foreground)/0.5)]">Question {index + 1} of {questions.length}</div>
      <div className="mt-2 text-sm font-medium">{text(current.label || current.question || current.title)}</div>
      <Textarea className="mt-3" value={answers[id] ?? ""} onChange={(event) => setAnswers((prev) => ({ ...prev, [id]: event.target.value }))} />
      <Button
        className="mt-3 w-full"
        onClick={() => last ? submitWidget("question-flow", title, "submit", answers, onSubmit) : setIndex((prev) => prev + 1)}
      >
        {last ? "Submit" : "Next"}
      </Button>
    </Wrap>
  );
}

export function ApprovalCardW({ title, data, onSubmit }: any) {
  return (
    <Wrap title={title}>
      <p className="text-sm text-[hsl(var(--foreground)/0.75)]">{text(data?.description || data?.message || data?.action || "Approve this action?")}</p>
      <div className="mt-4 flex gap-2">
        <Button className="flex-1" onClick={() => submitWidget("approval-card", title, "approved", { choice: "approved" }, onSubmit)}>
          <Check size={14} /> Approve
        </Button>
        <Button className="flex-1" variant="outline" onClick={() => submitWidget("approval-card", title, "denied", { choice: "denied" }, onSubmit)}>
          <X size={14} /> Deny
        </Button>
      </div>
    </Wrap>
  );
}

export function MessageDraftW({ title, data, onSubmit }: any) {
  const [draft, setDraft] = useState(text(data?.message || data?.draft || data?.content));
  return (
    <Wrap title={title}>
      <Textarea rows={5} value={draft} onChange={(event) => setDraft(event.target.value)} />
      <Button className="mt-3 w-full" onClick={() => submitWidget("message-draft", title, "send", { message: draft }, onSubmit)}>
        Submit draft
      </Button>
    </Wrap>
  );
}

export function OrderSummaryW({ title, data, onSubmit }: any) {
  const items = arrayFromData(data, ["items", "lineItems", "products"]);
  const total = data?.total ?? items.reduce((sum, item) => sum + Number(item.price ?? item.amount ?? 0) * Number(item.quantity ?? 1), 0);
  return (
    <Wrap title={title}>
      <div className="space-y-2">
        {items.map((item, index) => (
          <div key={item.id || index} className="flex items-center justify-between gap-3 text-sm">
            <span>{text(item.label || item.name || `Item ${index + 1}`)}</span>
            <span className="text-[hsl(var(--foreground)/0.65)]">{text(item.price ?? item.amount)}</span>
          </div>
        ))}
      </div>
      <div className="mt-3 flex items-center justify-between border-t border-[hsl(var(--glass-border))] pt-3 text-sm font-semibold">
        <span>Total</span>
        <span>{text(total)}</span>
      </div>
      <Button className="mt-3 w-full" onClick={() => submitWidget("order-summary", title, "confirm", { total, items }, onSubmit)}>
        Confirm
      </Button>
    </Wrap>
  );
}

export function CitationW({ title, data }: any) {
  const sources = arrayFromData(data, ["sources", "citations", "items"]);
  return (
    <Wrap title={title}>
      <div className="space-y-2">
        {sources.map((source, index) => (
          <a key={source.id || index} href={source.url || source.href} target="_blank" rel="noreferrer" className="block rounded-xl border border-[hsl(var(--glass-border))] px-3 py-2 text-sm hover:bg-[hsl(var(--surface-muted)/0.4)]">
            <div className="flex items-center justify-between gap-3">
              <span>{text(source.title || source.label || source.url || `Source ${index + 1}`)}</span>
              {(source.url || source.href) && <ExternalLink size={13} />}
            </div>
            {source.snippet && <p className="mt-1 text-xs text-[hsl(var(--foreground)/0.6)]">{source.snippet}</p>}
          </a>
        ))}
      </div>
    </Wrap>
  );
}

export function ItemCarouselW({ title, data }: any) {
  const items = arrayFromData(data, ["items", "cards", "results"]);
  return (
    <Wrap title={title}>
      <div className="flex gap-3 overflow-x-auto pb-1">
        {items.map((item, index) => (
          <div key={item.id || index} className="min-w-44 rounded-xl bg-[hsl(var(--surface-muted)/0.45)] p-3">
            {item.image && <img src={item.image} alt="" className="mb-2 h-24 w-full rounded-lg object-cover" />}
            <div className="text-sm font-medium">{text(item.title || item.label || `Item ${index + 1}`)}</div>
            {item.description && <div className="mt-1 text-xs text-[hsl(var(--foreground)/0.6)]">{item.description}</div>}
          </div>
        ))}
      </div>
    </Wrap>
  );
}

export function LinkPreviewW({ title, data }: any) {
  return (
    <Wrap title={title}>
      <a href={data?.url || data?.href} target="_blank" rel="noreferrer" className="flex gap-3 rounded-xl border border-[hsl(var(--glass-border))] p-3 hover:bg-[hsl(var(--surface-muted)/0.35)]">
        {data?.image && <img src={data.image} alt="" className="size-16 rounded-lg object-cover" />}
        <div className="min-w-0">
          <div className="truncate text-sm font-medium">{text(data?.title || data?.url)}</div>
          {data?.description && <div className="mt-1 line-clamp-2 text-xs text-[hsl(var(--foreground)/0.6)]">{data.description}</div>}
          <div className="mt-1 truncate text-[11px] text-[hsl(var(--foreground)/0.45)]">{text(data?.url || data?.href)}</div>
        </div>
      </a>
    </Wrap>
  );
}

export function TerminalW({ title, data }: any) {
  const lines = Array.isArray(data?.lines) ? data.lines.join("\n") : text(data?.output || data?.content || data);
  return (
    <Wrap title={title}>
      <pre className="max-h-72 overflow-auto rounded-xl bg-black/60 p-3 text-xs leading-relaxed text-green-100">{lines}</pre>
    </Wrap>
  );
}

export function WeatherWidgetW({ title, data }: any) {
  return (
    <Wrap title={title}>
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="text-sm text-[hsl(var(--foreground)/0.6)]">{text(data?.location)}</div>
          <div className="mt-1 text-3xl font-semibold">{text(data?.temperature ?? data?.temp)}{data?.unit || ""}</div>
          <div className="text-sm text-[hsl(var(--foreground)/0.7)]">{text(data?.condition || data?.summary)}</div>
        </div>
        {data?.icon && <img src={data.icon} alt="" className="size-16" />}
      </div>
    </Wrap>
  );
}

export function ChartW({ title, data }: any) {
  const chartType = text(data?.chartType || data?.type, "bar");
  const chartData = arrayFromData(data, ["data", "rows", "items", "series"]);
  if (chartType.includes("line")) return <Charts.LineChartW title={title} data={chartData} />;
  if (chartType.includes("donut") || chartType.includes("pie")) return <Charts.DonutChartW title={title} data={chartData} />;
  if (chartType.includes("scatter")) return <Charts.ScatterW title={title} data={chartData} />;
  return <Charts.BarChartW title={title} data={chartData} />;
}

export function CodeBlockW({ title, data }: any) {
  return (
    <Wrap title={title}>
      <pre className="max-h-96 overflow-auto rounded-xl bg-black/60 p-3 text-xs leading-relaxed text-slate-100"><code>{text(data?.code || data?.content)}</code></pre>
    </Wrap>
  );
}

export function CodeDiffW({ title, data }: any) {
  const diff = text(data?.diff || data?.content);
  return (
    <Wrap title={title}>
      <pre className="max-h-96 overflow-auto rounded-xl bg-black/60 p-3 text-xs leading-relaxed text-slate-100">
        {diff.split("\n").map((line, index) => (
          <div key={index} className={line.startsWith("+") ? "text-green-300" : line.startsWith("-") ? "text-red-300" : ""}>{line}</div>
        ))}
      </pre>
    </Wrap>
  );
}

export function SocialPostW({ title, data, platform }: any) {
  return (
    <Wrap title={title}>
      <div className="rounded-xl border border-[hsl(var(--glass-border))] p-3">
        <div className="mb-2 text-xs uppercase tracking-wide text-[hsl(var(--foreground)/0.5)]">{platform}</div>
        <p className="whitespace-pre-wrap text-sm leading-relaxed">{text(data?.text || data?.content || data?.caption)}</p>
        {data?.image && <img src={data.image} alt="" className="mt-3 max-h-72 w-full rounded-xl object-cover" />}
      </div>
    </Wrap>
  );
}

export function MediaW({ title, data, type }: any) {
  const src = data?.src || data?.url;
  return (
    <Wrap title={title}>
      {type === "audio" && <audio controls src={src} className="w-full" />}
      {type === "video" && <video controls src={src} poster={data?.poster} className="max-h-80 w-full rounded-xl" />}
      {type === "image" && <img src={src} alt={text(data?.alt || title)} className="max-h-96 w-full rounded-xl object-contain" />}
      {data?.caption && <div className="mt-2 text-xs text-[hsl(var(--foreground)/0.6)]">{data.caption}</div>}
    </Wrap>
  );
}

export function ImageGalleryW({ title, data }: any) {
  const images = arrayFromData(data, ["images", "items"]);
  return (
    <Wrap title={title}>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {images.map((image, index) => (
          <img key={image.id || index} src={image.src || image.url} alt={text(image.alt)} className="aspect-square rounded-xl object-cover" />
        ))}
      </div>
    </Wrap>
  );
}

export function GeoMapW({ title, data }: any) {
  const points = arrayFromData(data, ["points", "locations", "items"]);
  return (
    <Wrap title={title}>
      <div className="relative h-56 overflow-hidden rounded-xl bg-[hsl(var(--surface-muted)/0.45)]">
        <div className="absolute inset-0 opacity-30" style={{ backgroundImage: "linear-gradient(hsl(var(--glass-border)) 1px, transparent 1px), linear-gradient(90deg, hsl(var(--glass-border)) 1px, transparent 1px)", backgroundSize: "24px 24px" }} />
        {points.map((point, index) => {
          const x = Number(point.x ?? point.lng ?? point.longitude ?? 50);
          const y = Number(point.y ?? point.lat ?? point.latitude ?? 50);
          return (
            <div key={point.id || index} className="absolute -translate-x-1/2 -translate-y-1/2 rounded-full bg-[hsl(var(--primary))] px-2 py-1 text-[10px] text-primary-foreground" style={{ left: `${Math.max(4, Math.min(96, x))}%`, top: `${Math.max(4, Math.min(96, y))}%` }}>
              {text(point.label || point.name || index + 1)}
            </div>
          );
        })}
      </div>
    </Wrap>
  );
}
