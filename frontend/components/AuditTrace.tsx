import type { AuditEvent } from "@/types";

export default function AuditTrace({ events }: { events: AuditEvent[] }) {
  return (
    <section data-testid="audit-panel" className="rounded-xl border border-zinc-300 bg-white p-4">
      <h2 className="text-xs font-bold tracking-widest text-zinc-500">AUDIT TRACE</h2>
      <div className="mt-2 h-[560px] space-y-2 overflow-auto">
        {events.length === 0 && <p className="text-sm text-zinc-500">No events.</p>}
        {events.map((e) => (
          <div key={e.id} data-testid="audit-event" className="rounded border border-zinc-200 p-2 font-mono text-xs leading-5">
            <div className="font-bold">ACTION #{String(e.id).padStart(3, "0")} · {e.event_type}</div>
            {e.session_id && <div>Session: {e.session_id}</div>}
            {e.product_name && <div>Product: {e.product_name} (${e.price})</div>}
            {e.boundary_id && <div>Boundary: {e.boundary_id}</div>}
            {e.decision && <div>Decision: <b>{e.decision}</b></div>}
            {e.reason && <div>Reason: {e.reason}</div>}
            <div>Authority Source: {e.authority_source ?? "—"}</div>
            {e.tool_called && <div>MCP Tool: {e.tool_called}</div>}
            {e.tool_called && <div>Executed: {e.executed ? "YES" : "NO"}</div>}
          </div>
        ))}
      </div>
    </section>
  );
}
