import { Assistant } from "@/components/assistant/Assistant";

const Index = () => {
  return (
    <main className="min-h-screen relative overflow-hidden bg-background">
      {/* Ambient backdrop */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 left-1/3 w-[600px] h-[600px] rounded-full blur-3xl opacity-30"
          style={{ background: "radial-gradient(circle, hsl(var(--primary-glow)/0.4), transparent 70%)" }} />
        <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] rounded-full blur-3xl opacity-20"
          style={{ background: "radial-gradient(circle, hsl(var(--primary)/0.5), transparent 70%)" }} />
      </div>

      <header className="absolute top-0 left-0 right-0 p-6 flex items-center justify-between">
        <h1 className="text-sm font-semibold tracking-tight">Orb · Voice & Rich Chat</h1>
        <span className="text-xs text-muted-foreground">click · double-click · drag corner to resize</span>
      </header>

      <Assistant />
    </main>
  );
};

export default Index;
