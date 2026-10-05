import { useEffect, useRef } from "react";
import type { AgentReply } from "@/types";

export type Msg = { role: "user" | "agent" | "divider"; text: string; meta?: AgentReply };

const color: Record<string, string> = {
  ALLOW: "bg-emerald-100 text-emerald-800", ASK: "bg-amber-100 text-amber-800",
  BLOCK: "bg-red-100 text-red-800", DENIED: "bg-red-100 text-red-800",
};

export default function Chat({ session, msgs, input, setInput, onSend, onNew, busy }: {
  session: string; msgs: Msg[]; input: string; setInput: (s: string) => void;
  onSend: () => void; onNew: () => void; busy: boolean;
}) {
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => { end.current?.scrollIntoView({ block: "end" }); }, [msgs]);
  return (
    <section className="flex min-h-0 flex-1 flex-col rounded-xl border border-zinc-300 bg-white p-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-bold tracking-widest text-zinc-500">ALEXA+ SIMULATOR · <span data-testid="session-id">{session}</span></h2>
        <button data-testid="new-session" onClick={onNew} className="rounded border px-2 py-1 text-xs hover:bg-zinc-100">New Session</button>
      </div>
      <div className="mt-2 min-h-0 flex-1 space-y-2 overflow-auto">
        {msgs.map((m, i) => m.role === "divider" ? (
          <div key={i} data-testid="new-session-banner" className="rounded bg-sky-50 py-1 text-center text-xs font-bold tracking-widest text-sky-700">
            {m.text}
          </div>
        ) : (
          <div key={i} className={m.role === "user" ? "text-right" : ""}>
            <div data-testid={m.role === "user" ? "user-msg" : "agent-msg"}
              className={`inline-block max-w-[90%] rounded-lg px-3 py-1.5 text-sm ${m.role === "user" ? "bg-sky-600 text-white" : "bg-zinc-100"}`}>
              {m.text}
            </div>
            {m.meta?.product && (
              <div className="mt-1 text-xs text-zinc-600">
                Product: {m.meta.product.name} · ${m.meta.product.price} · {m.meta.product.merchant}
                {m.meta.product.subscription ? " · Subscription" : " · One-time"}
              </div>
            )}
            {m.meta?.decision && (
              <div className="mt-1 text-xs">
                <span data-testid="decision-badge" data-decision={m.meta.decision.decision}
                  className={`rounded px-1.5 py-0.5 font-bold ${color[m.meta.decision.decision]}`}>{m.meta.decision.decision === "DENIED" ? "DENIED" : m.meta.decision.decision === "BLOCK" ? "BLOCKED" : m.meta.decision.decision}</span>{" "}
                <span data-testid="decision-reason">{m.meta.decision.reason}</span>
                {Object.keys(m.meta.decision.checks).length > 0 && (
                  <span className="ml-2 font-mono text-zinc-500">
                    {Object.entries(m.meta.decision.checks).map(([k, v]) => `${k}:${v}`).join(" ")}
                  </span>
                )}
              </div>
            )}
            {m.meta?.authority_expansion && (
              <div data-testid="expansion-rejected" className="mt-1 rounded bg-red-600 px-2 py-1 text-xs font-bold tracking-wide text-white">
                AUTHORITY EXPANSION REJECTED
              </div>
            )}
            {m.meta?.decision?.decision === "ALLOW" && (
              <div data-testid="authority-source" className="mt-1 text-xs font-semibold text-emerald-700">
                Authority Source: Human Approval {m.meta.decision.boundary_id} · Agent-generated authority: NONE
              </div>
            )}
            {m.meta?.tool_action && (
              <div data-testid="order-status" className="mt-1 text-xs font-bold text-emerald-700">
                {m.meta.tool_action.result.status === "completed"
                  ? `PURCHASED · Order ${m.meta.tool_action.result.order_id} completed`
                  : "PURCHASE DENIED"}
              </div>
            )}
          </div>
        ))}
        <div ref={end} />
      </div>
      <form className="mt-2 flex gap-2" onSubmit={(e) => { e.preventDefault(); onSend(); }}>
        <input data-testid="chat-input" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Buy detergent for me."
          className="flex-1 rounded border px-3 py-2 text-sm" />
        <button data-testid="send" disabled={busy} className="rounded bg-zinc-900 px-4 py-2 text-sm text-white disabled:opacity-50">Send</button>
      </form>
    </section>
  );
}
