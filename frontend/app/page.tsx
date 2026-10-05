"use client";
import { useCallback, useEffect, useState } from "react";
import ApprovalPanel from "@/components/ApprovalPanel";
import AuditTrace from "@/components/AuditTrace";
import TracePanel from "@/components/TracePanel";
import Chat, { type Msg } from "@/components/Chat";
import { api } from "@/lib/api";
import type { AuditEvent, Boundary, TraceStep } from "@/types";

export default function Home() {
  const [session, setSession] = useState("…");
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [boundaries, setBoundaries] = useState<Boundary[]>([]);
  const [trace, setTrace] = useState<{ id: string | null; steps: TraceStep[] }>({ id: null, steps: [] });
  const [audit, setAudit] = useState<AuditEvent[]>([]);

  const refresh = useCallback(async () => {
    const [b, a] = await Promise.all([api.boundaries(), api.audit()]);
    setBoundaries(b);
    setAudit(a);
  }, []);

  const newSession = useCallback(async () => {
    const s = await api.newSession();
    setSession(s.id);
    setMsgs((m) => [...m, ...(s.boundaries.length || m.length === 0 ? [{ role: "divider" as const, text: `NEW SESSION ${s.id}` }] : []), { role: "agent", text: s.boundaries.length
      ? `Session ${s.id}: loaded existing human-approved authority ${s.boundaries.map((b) => b.id).join(", ")}.`
      : `Session ${s.id}: no approved authority yet.` }]);
    await refresh();
  }, [refresh]);

  useEffect(() => { newSession(); }, [newSession]);

  const send = async () => {
    const text = input.trim();
    if (!text || busy) return;
    setInput(""); setBusy(true);
    setMsgs((m) => [...m, { role: "user", text }]);
    try {
      const r = await api.message(session, text);
      setMsgs((m) => [...m, { role: "agent", text: r.reply, meta: r }]);
      setTrace({ id: r.trace_id, steps: r.trace });
    } catch (e) {
      setMsgs((m) => [...m, { role: "agent", text: `Error: ${e}` }]);
    }
    setBusy(false);
    refresh();
  };

  const proposal = boundaries.filter((b) => b.status === "PROPOSED").at(-1) ?? null;
  const active = boundaries.filter((b) => b.status === "ACTIVE");

  return (
    <main className="mx-auto max-w-[1280px] p-4">
      <div className="mb-2">
        <h1 className="text-lg font-bold">Bounded Autonomy for Alexa+</h1>
        <p data-testid="why-alexa" className="text-xs text-zinc-600">Why Alexa+? Alexa+ acts across services and sessions — Bounded Autonomy gives it a persistent, human-approved authority envelope.</p>
      </div>
      <div className="grid h-[690px] gap-3 lg:grid-cols-[1.4fr_1fr_1fr]">
        <div className="flex min-h-0 flex-col gap-3">
        <Chat session={session} msgs={msgs} input={input} setInput={setInput} onSend={send} onNew={newSession} busy={busy} />
        <TracePanel id={trace.id} steps={trace.steps} />
        </div>
        <ApprovalPanel proposal={proposal} active={active}
          onApprove={async () => { await api.approve(proposal!.id, session); await refresh();
            setMsgs((m) => [...m, { role: "agent", text: `Boundary ${proposal!.id} approved by you. Start a New Session to see it persist.` }]); }}
          onReject={async () => { await api.reject(proposal!.id, session); await refresh(); }} />
        <div className="flex min-h-0 flex-col gap-2">
          <AuditTrace events={audit} />
          <button data-testid="reset-demo" onClick={async () => { await api.reset(); setMsgs([]); setTrace({ id: null, steps: [] }); await newSession(); }}
            className="w-full rounded border border-red-300 px-3 py-1.5 text-sm text-red-700 hover:bg-red-50">Reset Demo</button>
        </div>
      </div>
    </main>
  );
}
