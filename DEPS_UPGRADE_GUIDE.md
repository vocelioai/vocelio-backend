# Dependency Governance & Upgrade Guide

This document explains how to safely update shared dependencies across all Vocelio microservices under the new centralized constraints model.

## 1. Core Concepts

- `constraints.txt` is the single source of truth for versions of core, shared libraries (FastAPI stack, httpx, pydantic, etc.).
- Service `requirements.txt` files reference it via `-c ../../constraints.txt` (or `-c constraints.txt` at root) and omit versions for pinned packages.
- Upgrading a core dependency requires only editing `constraints.txt` followed by CI verification.

## 2. Upgrade Workflow (Checklist)

1. Create a feature branch: `feat/upgrade-fastapi-<new_version>`.
2. Edit `constraints.txt` updating the target version (e.g. `fastapi==0.113.0`). Keep related transitive pins (starlette, pydantic) coherent.
3. Run local validation:
   - `pip install -r requirements.txt` (root)
   - Loop through service requirement files: `for f in apps/*/requirements.txt; do pip install -r $f; done` (WSL/Mac) or PowerShell equivalent.
4. Run test suite & lint locally.
5. Commit changes with a conventional commit message: `chore(deps): bump fastapi to 0.113.0`.
6. Push branch & open PR.
7. Ensure CI matrix (3.11 & 3.13) passes.
8. Merge PR after approvals.
9. Trigger deployments on Railway if needed.

## 3. Version Cohesion Notes

- FastAPI upgrades may require matching `starlette` & `pydantic` adjustments (consult FastAPI release notes).
- `httpx` must remain `<0.26` while Supabase libs depend on older httpx APIs. Upgrade Supabase client first before raising httpx.
- `pydantic` major/minor bumps often require code refactors (model config syntax). Test thoroughly.
- Keep `uvicorn` and `fastapi` within 1-2 minor versions for ASGI compatibility.

## 4. Adding a New Shared Pin

Only add to `constraints.txt` if: 
- The package is used (same major line) in >= 3 services; and
- Divergent versions have caused (or could cause) resolver or runtime conflicts; and
- Pinning will not block needed service-specific experimentation.

Process:
1. Confirm usage count with a quick grep.
2. Decide target version (prefer latest compatible minor).
3. Add to `constraints.txt`.
4. Remove explicit version from all service `requirements.txt` (if present).
5. Install + test.

## 5. Removing a Pin

If experimentation is needed, remove the line from `constraints.txt` and explicitly version desired services. Document rationale in PR.

## 6. Emergency Rollback

1. Revert commit modifying `constraints.txt` (or edit to previous versions).
2. Re-run CI.
3. Merge hotfix branch.
4. Confirm production containers redeploy with prior versions.

## 7. Tooling Enhancements (Future)

- Add a script (e.g. `scripts/check_pins.py`) that fails CI if a service reintroduces a version for a pinned package.
- Automate dependency diff in PR description using a GitHub Action.
- Weekly scheduled job that upgrades minor/patch versions in a dry-run and opens an automated PR.

### Current Governance Tools

- `constraints.txt` — authoritative shared versions.
- `scripts/check_pins.py` — detects re-pins (run manually or in CI).
- `.env.example` — sanitized template; never commit real `.env`.

Add this CI step after installs to enforce central pins:

```yaml
- name: Enforce central pins
  run: python scripts/check_pins.py
```

If it fails:
1. Add `-c ../../constraints.txt` (or correct relative path) to the top of the offending service `requirements.txt`.
2. Remove any `pkg==version` where `pkg` appears in `constraints.txt` (preserve extras like `[http2]` but drop version & extras pinning).
3. Remove duplicates (e.g., multiple python-dotenv lines).
4. Re-run the checker locally.

Secret exposure remediation (if `.env` with real keys was committed):
1. Immediately `git rm .env` and commit.
2. Rotate all exposed keys (OpenAI, Stripe, Twilio, Supabase, JWT secrets, webhook secrets).
3. Invalidate prior JWTs if feasible by changing signing secret.
4. Audit access logs for suspicious activity during exposure window.

## 8. PowerShell Loop Examples

Install all services (current folder root):
```powershell
Get-ChildItem apps -Directory | ForEach-Object { 
  $req = Join-Path $_.FullName 'requirements.txt';
  if (Test-Path $req) { pip install -r $req }
}
```

Dry-run resolution for all services:
```powershell
Get-ChildItem apps -Directory | ForEach-Object { 
  $req = Join-Path $_.FullName 'requirements.txt';
  if (Test-Path $req) { Write-Host "Checking $req"; pip install -r $req --dry-run > $null }
}
```

## 9. Release Communication Template

```
Chore: Upgrade FastAPI stack
- fastapi: 0.112.2 -> 0.113.0
- starlette: 0.37.2 -> 0.38.x
- pydantic: 2.8.2 -> 2.9.1
Validation:
- CI matrix green (3.11, 3.13)
- Smoke tested api-gateway & smart-campaigns locally
Risk Mitigation:
- Rollback = revert constraints.txt commit
```

## 10. Common Pitfalls

- Forgetting to add `-c ../../constraints.txt` after creating a new service.
- Pinning a core dependency in a new service (causes potential drift). Remove the version.
- Upgrading httpx without verifying Supabase client compatibility.
- Ignoring transitive changes (e.g., starlette bump when raising fastapi major/minor).

## 11. Questions

Document clarifications inline in this file via PRs to keep the process living and accurate.

---
Maintainer: Platform Engineering
Last Updated: 2025-08-10
