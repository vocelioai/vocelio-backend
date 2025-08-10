## Security Notice: Exposed Secrets Remediation

The file `.env` containing production-like secrets (API keys, JWT secrets, Stripe/Twilio keys, Supabase key) was committed to the repository. Even after removal, those secrets remain in the Git history and must be considered compromised.

### Immediate Required Actions
1. Rotate ALL exposed credentials:
   - Supabase service role / anon keys
   - OpenAI API key (project key)
   - ElevenLabs API key
   - Twilio Auth Token (SID itself is public identifier; rotate token)
   - Stripe Secret + Webhook + Publishable keys
   - JWT_SECRET_KEY / SECRET_KEY (generate new random 64+ byte values; invalidate old tokens)
   - Any other third-party keys (Ramble, etc.)
2. Deploy updated secrets to all environments (Railway, staging, production) BEFORE invalidating old ones where possible to avoid downtime.
3. Invalidate previous JWTs by changing signing key and (optionally) enforcing re-auth flows.
4. Audit access logs for unusual activity during exposure window.

### Optional (Recommended) History Cleanup
To excise plaintext secrets from history:
1. Ensure rotated secrets exist ONLY in secret manager / env vars, not the repo.
2. Use one of:
   - `git filter-repo --path .env --invert-paths`
   - OR BFG: `bfg --delete-files .env`
3. Force push cleaned history: `git push --force-with-lease origin main`.
4. Notify all developers to re-clone (old clones still contain the data).

### Prevention
1. `.gitignore` already ignores `.env`; keep it that way.
2. Add secret scanning + pin check pre-commit hooks.
3. Never place production secrets in example files—only placeholders.

### Example .pre-commit-config.yaml Additions
```yaml
repos:
  - repo: https://github.com/zricethezav/gitleaks
    rev: v8.18.4
    hooks:
      - id: gitleaks
  - repo: local
    hooks:
      - id: pin-check
        name: Enforce central dependency pins
        entry: python scripts/check_pins.py
        language: system
        pass_filenames: false
```
Install:
```
pip install pre-commit
pre-commit install
```

### Timeline
- Detection: During dependency governance cleanup.
- Notice Added: 2025-08-10

### Owner
Platform / DevOps Team

Rotate first, then (optionally) clean history. Treat all exposed credentials as compromised until replaced.
