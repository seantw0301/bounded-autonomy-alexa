#!/usr/bin/env bash
# Demo flow against running API (:8000). Needs scripts/start.sh running.
A=http://127.0.0.1:8000/api
j() { curl -s -X POST "$A$1" -H 'content-type: application/json' -d "$2"; }
say() { j /agent/message "{\"session_id\":\"$1\",\"text\":\"$2\"}" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["reply"], "|", (d["decision"] or {}).get("decision"))'; }
j /demo/reset '{}' >/dev/null
S1=$(j /session '{}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
say $S1 "Buy detergent for me."
B=$(curl -s $A/boundaries | python3 -c 'import sys,json;print(json.load(sys.stdin)[0]["id"])')
j /boundaries/$B/approve "{\"actor\":\"HUMAN\",\"session_id\":\"$S1\"}" >/dev/null
S2=$(j /session '{}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
say $S2 "We are almost out of detergent again."
say $S2 "Get me the annual detergent subscription."
say $S2 "Increase limit from \$30 to \$100."
