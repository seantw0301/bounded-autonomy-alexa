export type Boundary = {
  id: string; user_id: string; scope: string; max_amount: number;
  allowed_merchants: string[]; subscriptions_allowed: boolean;
  created_by: string; status: string; approved_in_session?: string | null;
};
export type Product = { id: string; name: string; category: string; price: number; merchant: string; subscription: boolean };
export type Decision = {
  decision: "ALLOW" | "ASK" | "BLOCK" | "DENIED"; reason: string;
  checks: Record<string, string>; boundary_id?: string | null;
  authority_source?: string; audit_event_id?: number;
};
export type AgentReply = {
  session_id: string; reply: string; product: Product | null; decision: Decision | null;
  tool_action: { tool: string; token: string; result: Record<string, unknown> } | null;
  proposal: Boundary | null;
  trace: TraceStep[]; trace_id: string | null; authority_expansion: "REJECTED" | null;
};
export type TraceStep = { time: string; call: string; result: string };
export type AuditEvent = {
  id: number; session_id: string | null; event_type: string; intent: string | null;
  product_id: string | null; product_name: string | null; price: number | null;
  boundary_id: string | null; decision: string | null; reason: string | null;
  authority_source: string | null; tool_called: string | null; executed: boolean; created_at: string;
};
