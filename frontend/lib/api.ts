async function req<T>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(`/api${path}`, {
    method: body === undefined ? "GET" : "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json();
}
export const api = {
  newSession: () => req<{ id: string; boundaries: import("@/types").Boundary[] }>("/session", {}),
  message: (session_id: string, text: string) =>
    req<import("@/types").AgentReply>("/agent/message", { session_id, text }),
  boundaries: () => req<import("@/types").Boundary[]>("/boundaries"),
  approve: (id: string, session_id: string) =>
    req<import("@/types").Boundary>(`/boundaries/${id}/approve`, { actor: "HUMAN", session_id }),
  reject: (id: string, session_id: string) =>
    req<import("@/types").Boundary>(`/boundaries/${id}/reject`, { actor: "HUMAN", session_id }),
  audit: () => req<import("@/types").AuditEvent[]>("/audit"),
  reset: () => req<unknown>("/demo/reset", {}),
};
