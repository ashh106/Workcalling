import {
  Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart,
  PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer,
  Scatter, ScatterChart, Tooltip, Treemap, XAxis, YAxis, Area, AreaChart,
  FunnelChart, Funnel, LabelList,
} from "recharts";

const c = {
  primary: "hsl(var(--primary))",
  glow: "hsl(var(--primary-glow))",
  muted: "hsl(var(--surface-muted))",
  fg: "hsl(var(--surface-foreground))",
  border: "hsl(var(--surface-border))",
};

const tooltipStyle = {
  background: "hsl(var(--surface))",
  border: `1px solid ${c.border}`,
  borderRadius: 12,
  color: c.fg,
  fontSize: 12,
};

const Wrap = ({ title, children, height = 220 }: any) => (
  <div className="rounded-2xl bg-[hsl(var(--surface-input))] p-4 border border-[hsl(var(--surface-border))]">
    {title && <div className="text-xs font-medium text-[hsl(var(--surface-foreground))]/70 mb-2">{title}</div>}
    <div style={{ width: "100%", height }}>{children}</div>
  </div>
);

export function BarChartW({ title, data }: any) {
  return (
    <Wrap title={title}>
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid stroke={c.border} strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" stroke={c.fg} fontSize={11} tickLine={false} axisLine={false} />
          <YAxis stroke={c.fg} fontSize={11} tickLine={false} axisLine={false} />
          <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "hsl(var(--primary)/0.1)" }} />
          <Bar dataKey="value" fill={c.primary} radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Wrap>
  );
}

export function LineChartW({ title, data }: any) {
  return (
    <Wrap title={title}>
      <ResponsiveContainer>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="lg" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={c.primary} stopOpacity={0.4} />
              <stop offset="100%" stopColor={c.primary} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke={c.border} strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" stroke={c.fg} fontSize={11} tickLine={false} axisLine={false} />
          <YAxis stroke={c.fg} fontSize={11} tickLine={false} axisLine={false} />
          <Tooltip contentStyle={tooltipStyle} />
          <Area type="monotone" dataKey="value" stroke={c.primary} strokeWidth={2} fill="url(#lg)" dot={{ fill: c.glow, r: 3 }} />
        </AreaChart>
      </ResponsiveContainer>
    </Wrap>
  );
}

export function DonutChartW({ title, data }: any) {
  const total = data.reduce((s: number, d: any) => s + d.value, 0);
  const colors = [c.primary, c.glow, "hsl(222 60% 40%)", "hsl(222 30% 60%)", "hsl(222 80% 75%)"];
  return (
    <Wrap title={title}>
      <div className="relative w-full h-full">
        <ResponsiveContainer>
          <PieChart>
            <Pie data={data} dataKey="value" innerRadius="60%" outerRadius="85%" paddingAngle={2}>
              {data.map((_: any, i: number) => <Cell key={i} fill={colors[i % colors.length]} stroke="none" />)}
            </Pie>
            <Tooltip contentStyle={tooltipStyle} />
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <div className="text-xl font-semibold">{total.toLocaleString()}</div>
          <div className="text-xs opacity-60">Total</div>
        </div>
      </div>
    </Wrap>
  );
}

export function RadarW({ title, data }: any) {
  return (
    <Wrap title={title}>
      <ResponsiveContainer>
        <RadarChart data={data}>
          <PolarGrid stroke={c.border} />
          <PolarAngleAxis dataKey="name" stroke={c.fg} fontSize={11} />
          <Radar dataKey="value" stroke={c.primary} fill={c.primary} fillOpacity={0.3} />
          <Tooltip contentStyle={tooltipStyle} />
        </RadarChart>
      </ResponsiveContainer>
    </Wrap>
  );
}

export function ScatterW({ title, data }: any) {
  return (
    <Wrap title={title}>
      <ResponsiveContainer>
        <ScatterChart>
          <CartesianGrid stroke={c.border} strokeDasharray="3 3" />
          <XAxis dataKey="x" stroke={c.fg} fontSize={11} />
          <YAxis dataKey="y" stroke={c.fg} fontSize={11} />
          <Tooltip contentStyle={tooltipStyle} cursor={{ strokeDasharray: "3 3" }} />
          <Scatter data={data} fill={c.primary} />
        </ScatterChart>
      </ResponsiveContainer>
    </Wrap>
  );
}

export function HeatmapW({ title, data }: { title?: string; data: { rows: string[]; cols: string[]; values: number[][] } }) {
  const max = Math.max(...data.values.flat());
  return (
    <Wrap title={title} height={undefined as any}>
      <div className="grid gap-1" style={{ gridTemplateColumns: `auto repeat(${data.cols.length}, 1fr)` }}>
        <div />
        {data.cols.map((col) => <div key={col} className="text-[10px] text-center opacity-60">{col}</div>)}
        {data.rows.flatMap((row, ri) => [
          <div key={`r-${row}`} className="text-[10px] opacity-60 pr-2 self-center">{row}</div>,
          ...data.values[ri].map((v, ci) => (
            <div key={`c-${ri}-${ci}`} className="aspect-square rounded" style={{ background: `hsl(var(--primary) / ${v / max})` }} title={`${v}`} />
          )),
        ])}
      </div>
    </Wrap>
  );
}

export function FunnelW({ title, data }: any) {
  return (
    <Wrap title={title} height={260}>
      <ResponsiveContainer>
        <FunnelChart>
          <Tooltip contentStyle={tooltipStyle} />
          <Funnel dataKey="value" data={data} isAnimationActive>
            {data.map((_: any, i: number) => (
              <Cell key={i} fill={`hsl(222 ${85 - i * 10}% ${60 - i * 6}%)`} />
            ))}
            <LabelList position="right" fill={c.fg} stroke="none" dataKey="name" fontSize={11} />
          </Funnel>
        </FunnelChart>
      </ResponsiveContainer>
    </Wrap>
  );
}

export function WaterfallW({ title, data }: any) {
  // expects [{name, value, type: 'start'|'pos'|'neg'|'total'}]
  let acc = 0;
  const computed = data.map((d: any) => {
    if (d.type === "start" || d.type === "total") {
      const r = { ...d, base: 0, height: d.value };
      acc = d.value;
      return r;
    }
    const base = d.value >= 0 ? acc : acc + d.value;
    const r = { ...d, base, height: Math.abs(d.value) };
    acc += d.value;
    return r;
  });
  return (
    <Wrap title={title}>
      <ResponsiveContainer>
        <BarChart data={computed}>
          <CartesianGrid stroke={c.border} strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" stroke={c.fg} fontSize={11} />
          <YAxis stroke={c.fg} fontSize={11} />
          <Tooltip contentStyle={tooltipStyle} />
          <Bar dataKey="base" stackId="a" fill="transparent" />
          <Bar dataKey="height" stackId="a" radius={[4, 4, 0, 0]}>
            {computed.map((d: any, i: number) => (
              <Cell key={i} fill={d.type === "neg" ? "hsl(0 70% 55%)" : d.type === "total" || d.type === "start" ? c.glow : c.primary} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Wrap>
  );
}

export function TreemapW({ title, data }: any) {
  return (
    <Wrap title={title}>
      <ResponsiveContainer>
        <Treemap data={data} dataKey="value" stroke="hsl(var(--surface))" fill={c.primary} />
      </ResponsiveContainer>
    </Wrap>
  );
}

export function SparklineW({ title, data }: any) {
  const last = data[data.length - 1]?.value ?? 0;
  const first = data[0]?.value ?? 0;
  const delta = first ? (((last - first) / first) * 100).toFixed(0) : "0";
  return (
    <Wrap title={title} height={120}>
      <div className="flex items-center gap-3 h-full">
        <div className="flex-1 h-full">
          <ResponsiveContainer>
            <LineChart data={data}>
              <Line type="monotone" dataKey="value" stroke={c.primary} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="text-lg font-semibold text-[hsl(var(--primary-glow))]">+{delta}%</div>
      </div>
    </Wrap>
  );
}

export function SankeyW({ title, data }: any) {
  // simple proportional flow rendering
  const max = Math.max(...data.map((d: any) => d.value));
  return (
    <Wrap title={title}>
      <div className="space-y-2">
        {data.map((d: any) => (
          <div key={d.name} className="flex items-center gap-3">
            <div className="text-xs w-24 opacity-70">{d.name}</div>
            <div className="flex-1 h-8 rounded-full bg-[hsl(var(--surface-muted))] overflow-hidden">
              <div className="h-full rounded-full bg-gradient-to-r from-[hsl(var(--primary))] to-[hsl(var(--primary-glow))] flex items-center px-3 text-xs"
                style={{ width: `${(d.value / max) * 100}%` }}>
                ${d.value.toLocaleString()}
              </div>
            </div>
          </div>
        ))}
      </div>
    </Wrap>
  );
}

export function NetworkW({ title, data }: { title?: string; data: { nodes: { id: string; x: number; y: number; main?: boolean }[]; edges: [string, string][] } }) {
  const map = Object.fromEntries(data.nodes.map((n) => [n.id, n]));
  return (
    <Wrap title={title}>
      <svg viewBox="0 0 100 100" className="w-full h-full">
        {data.edges.map(([a, b], i) => (
          <line key={i} x1={map[a].x} y1={map[a].y} x2={map[b].x} y2={map[b].y} stroke={c.border} strokeWidth={0.4} />
        ))}
        {data.nodes.map((n) => (
          <g key={n.id}>
            <circle cx={n.x} cy={n.y} r={n.main ? 5 : 3.5} fill={n.main ? c.primary : c.muted} stroke={c.glow} strokeWidth={n.main ? 0.8 : 0} />
            <text x={n.x} y={n.y + 1} textAnchor="middle" fontSize={3} fill={c.fg}>{n.id}</text>
          </g>
        ))}
      </svg>
    </Wrap>
  );
}
