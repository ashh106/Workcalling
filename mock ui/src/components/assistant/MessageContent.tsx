import { AssistantMessage } from "./widgets/types";
import { WidgetRenderer } from "./widgets/WidgetRenderer";

function renderInline(text: string) {
  // bold **x** and lists handled at block level
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((p, i) =>
    p.startsWith("**") ? <strong key={i} className="font-semibold">{p.slice(2, -2)}</strong> : <span key={i}>{p}</span>
  );
}

function renderText(text: string) {
  const lines = text.split("\n");
  const out: JSX.Element[] = [];
  let bullets: string[] = [];
  const flush = () => {
    if (bullets.length) {
      out.push(
        <ul key={out.length} className="list-disc pl-5 space-y-1 text-sm leading-relaxed">
          {bullets.map((b, i) => <li key={i}>{renderInline(b)}</li>)}
        </ul>
      );
      bullets = [];
    }
  };
  for (const ln of lines) {
    if (/^\s*[-•]\s+/.test(ln)) bullets.push(ln.replace(/^\s*[-•]\s+/, ""));
    else {
      flush();
      if (ln.trim()) out.push(<p key={out.length} className="text-sm leading-relaxed">{renderInline(ln)}</p>);
    }
  }
  flush();
  return <div className="space-y-2">{out}</div>;
}

export function MessageContent({ message }: { message: AssistantMessage }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="rounded-full orb-gradient px-5 py-2 text-sm text-primary-foreground max-w-[80%] shadow-lg">
          {message.blocks[0]?.text}
        </div>
      </div>
    );
  }
  return (
    <div className="space-y-3">
      {message.blocks.map((b, i) => (
        <div key={i}>
          {b.kind === "text" && b.text && renderText(b.text)}
          {b.kind === "widget" && b.widget && <WidgetRenderer widget={b.widget} />}
        </div>
      ))}
    </div>
  );
}
