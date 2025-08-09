import sys, os, json, time
import httpx

GATEWAY = os.environ.get("GATEWAY_URL", "http://localhost:8000")
SERVICES = ["overview-service", "ai-agents-service", "smart-campaigns-service"]

results = {"gateway": {}, "services": {}}

print(f"[smoke] Testing gateway {GATEWAY}")

with httpx.Client(timeout=5.0) as client:
    r = client.get(f"{GATEWAY}/health")
    results["gateway"]["health"] = r.status_code
    r2 = client.get(f"{GATEWAY}/health/detailed")
    results["gateway"]["detailed_keys"] = list(r2.json().keys())

    for svc in SERVICES:
        url = f"{GATEWAY}/api/{svc}/health"
        try:
            rs = client.get(url)
            results["services"][svc] = {"status": rs.status_code}
        except Exception as e:
            results["services"][svc] = {"error": str(e)}

print(json.dumps(results, indent=2))

failed = any(v.get("status") != 200 for v in results["services"].values())
if failed:
    print("[smoke] One or more service health checks failed", file=sys.stderr)
    sys.exit(1)
print("[smoke] Success")
