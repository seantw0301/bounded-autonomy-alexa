import type { TraceStep } from "@/types";

export default function TracePanel({ id, steps }: { id: string | null; steps: TraceStep[] }) {
  return (
    <section data-testid="mcp-trace" className="rounded-xl border border-zinc-300 bg-zinc-950 p-3 text-zinc-100">
      <h2 className="text-xs font-bold tracking-widest text-zinc-400">MCP TRACE {id ? `#${id}` : ""}</h2>
      <div className="mt-1 h-36 overflow-auto font-mono text-[11px] leading-5">
        {steps.length === 0 && <p className="text-zinc-500">No tool calls yet.</p>}
        {steps.map((s, i) => (
          <div key={i} data-testid="trace-step">
            <span className="text-zinc-500">{s.time}</span> <span className="text-sky-300">{s.call}</span>
            <div className="pl-[4.5rem] text-emerald-300">→ {s.result}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
