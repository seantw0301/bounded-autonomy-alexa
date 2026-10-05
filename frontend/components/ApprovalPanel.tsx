import type { Boundary } from "@/types";

export function BoundaryCard({ b }: { b: Boundary }) {
  return (
    <div className="text-sm space-y-0.5">
      <div className="font-semibold">{b.scope.split("_").map((w) => w[0].toUpperCase() + w.slice(1)).join(" ")}</div>
      <div>≤ ${b.max_amount} / purchase</div>
      <div>{b.allowed_merchants.join(" / ")}</div>
      <div>{b.subscriptions_allowed ? "Subscriptions allowed" : "No Subscriptions"}</div>
    </div>
  );
}

export default function ApprovalPanel({ proposal, active, onApprove, onReject }: {
  proposal: Boundary | null; active: Boundary[];
  onApprove: () => void; onReject: () => void;
}) {
  return (
    <section className="h-full overflow-auto rounded-xl border border-zinc-300 bg-white p-4">
      <h2 className="text-xs font-bold tracking-widest text-amber-700">HUMAN APPROVAL REQUIRED</h2>
      {proposal ? (
        <div data-testid="proposal" className="mt-2 space-y-3">
          <div className="text-xs text-zinc-500">Proposed Autonomy Boundary · {proposal.id}</div>
          <BoundaryCard b={proposal} />
          <div className="flex gap-2">
            <button data-testid="reject-boundary" onClick={onReject} className="flex-1 rounded border px-3 py-1.5 text-sm hover:bg-zinc-100">Reject</button>
            <button data-testid="approve-boundary" onClick={onApprove} className="flex-1 rounded bg-emerald-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-emerald-700">Approve</button>
          </div>
        </div>
      ) : (
        <p className="mt-2 text-sm text-zinc-500">No pending proposal.</p>
      )}
      <h3 className="mt-4 text-xs font-bold tracking-widest text-zinc-500">CURRENT AUTHORITY</h3>
      <div data-testid="current-authority">
        {active.length === 0 && <p className="mt-1 text-sm text-zinc-500">None — no approved authority</p>}
        {active.map((b) => (
          <div key={b.id} data-testid="active-boundary" className="mt-2 rounded bg-emerald-50 p-2">
            <div className="text-xs font-semibold text-emerald-800">{b.id} · ACTIVE · Approved by {b.created_by === "HUMAN" ? "Human" : b.created_by}</div>
            <BoundaryCard b={b} />
            <div className="mt-1 text-xs text-emerald-800">Approved in Session {b.approved_in_session ?? "—"}</div>
            <div className="text-xs text-emerald-800">Agent-generated authority: NONE</div>
          </div>
        ))}
      </div>
    </section>
  );
}
