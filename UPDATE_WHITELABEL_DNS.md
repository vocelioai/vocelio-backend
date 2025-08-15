# 🔧 White-Label DNS Update Guide

## New Railway URL
**Service**: White-Label Service  
**New URL**: `ttn13i41.up.railway.app`  
**Custom Domain**: `whitelabel.vocelio.ai`

## DNS Configuration Required

### 1. Update CNAME Record
Go to your DNS provider (Cloudflare, etc.) and update:

```
Type: CNAME
Name: whitelabel
Target: ttn13i41.up.railway.app
TTL: Auto (or 300 seconds for faster propagation)
```

### 2. Current DNS Status
- **Issue**: DNS not resolving `whitelabel.vocelio.ai`
- **Cause**: CNAME record needs to point to new Railway URL
- **Fix**: Update CNAME record from old URL to `ttn13i41.up.railway.app`

## Verification Steps

### Test the Raw Railway URL
```powershell
curl "https://ttn13i41.up.railway.app/"
```

### Test DNS Resolution
```powershell
nslookup whitelabel.vocelio.ai
```

### Test Custom Domain (after DNS update)
```powershell
curl "https://whitelabel.vocelio.ai/"
```

## Expected Results
- ✅ Railway URL should respond with service content
- ✅ DNS should resolve to Railway IP
- ✅ Custom domain should work after propagation (5-30 minutes)

## Action Required
1. **Update DNS CNAME**: `whitelabel → ttn13i41.up.railway.app`
2. **Wait for propagation**: 5-30 minutes
3. **Test domain**: `https://whitelabel.vocelio.ai`

---
*DNS propagation typically takes 5-30 minutes globally*
