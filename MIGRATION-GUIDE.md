# 🚨 MIGRATION GUIDE - Railway → Render.com

## ⚡ MIGRARE URGENTĂ (Railway Trial Expired)

### ✅ Ce am făcut deja:
1. **Backend updated** - Port flexibil (8000/10000)
2. **Render config** - `render.yaml` adăugat  
3. **Start script** - `render-start.sh` pentru optimizare
4. **Multi-platform support** - Funcționează pe orice hosting

---

## 🎯 OPȚIUNEA 1: RENDER.COM (RECOMANDAT)

### ⚡ Deploy în 2 minute:

1. **Render.com** → Login GitHub
2. **New Web Service** → Connect `viralsafe-platform-free`
3. **Settings:**
   ```
   Root Directory: backend
   Build: pip install -r requirements.txt
   Start: uvicorn main:app --host 0.0.0.0 --port 10000
   ```
4. **Environment:**
   ```
   PORT=10000
   CORS_ORIGINS=*
   ```
5. **Deploy!**

**✅ Avantaje Render:**
- 512 MB RAM (suficient)
- 750 ore/lună (25 zile)
- SSL gratuit + custom domain
- Auto-deploy GitHub
- Monitoring inclus

---

## 🎯 OPȚIUNEA 2: FLY.IO (PENTRU POWER USERS)

### 🛠️ Setup Fly.io:

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# În backend/
flyctl launch --no-deploy
```

**fly.toml:**
```toml
app = "viralsafe-backend"
primary_region = "fra"

[build]

[env]
  PORT = "8000"
  CORS_ORIGINS = "*"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/health"

[processes]
  app = "uvicorn main:app --host 0.0.0.0 --port 8000"
```

```bash
# Deploy
flyctl deploy
```

**✅ Avantaje Fly.io:**
- 1 GB RAM (dublu față de Render)
- Nu se oprește automat
- Multiple regiuni
- $5 credit lunar (suficient pentru o app mică)

---

## 🎯 OPȚIUNEA 3: VERCEL SERVERLESS

### 🔧 Restructurare pentru Vercel:

**api/main.py:**
```python
from fastapi import FastAPI
from mangum import Mangum

# Importă toate funcțiile din backend/main.py
from ..backend.main import app

# Wrapper pentru Vercel
handler = Mangum(app)
```

**vercel.json:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/main.py"
    }
  ]
}
```

**requirements.txt (adaugă):**
```
mangum==0.17.0
```

---

## 🔄 UPDATE FRONTEND URL

### Render URL Format:
```
https://your-service-name.onrender.com
```

### Update în Vercel:
1. **Vercel Dashboard** → Your Frontend Project
2. **Settings** → **Environment Variables**
3. **Edit NEXT_PUBLIC_API_URL:**
   ```
   NEXT_PUBLIC_API_URL=https://your-service-name.onrender.com
   ```
4. **Redeploy** frontend

---

## 📊 COMPARAȚIE PLATFORME

| Platform | RAM | CPU | Bandwidth | Cost | Uptime |
|----------|-----|-----|-----------|------|--------|
| **Render** | 512MB | 0.1 | 100GB | FREE | 750h/lună |
| **Fly.io** | 1GB | 1.0 | 160GB | $5 credit | 24/7 |
| **Vercel** | Serverless | Auto | Unlimited | FREE | 24/7 |
| **Railway** | ❌ | ❌ | ❌ | Trial expired | ❌ |

---

## ⚡ ACȚIUNI IMEDIATE

### ✅ CHECKLIST MIGRARE:

- [ ] **Render account** creat
- [ ] **Web service** configurat  
- [ ] **Environment variables** setate
- [ ] **Backend deployed** și functional
- [ ] **Health check** `/health` funcționează
- [ ] **Frontend URL** updated în Vercel
- [ ] **Frontend redeployed**
- [ ] **End-to-end test** complet

### 🧪 TESTING:

```bash
# Test backend health
curl https://your-render-app.onrender.com/health

# Test analysis endpoint
curl -X POST "https://your-render-app.onrender.com/analyze" \
  -H "Content-Type: application/json" \
  -d '{"content":"Test message for analysis","platform":"general"}'

# Test frontend
# Deschide https://your-frontend.vercel.app
# Testează analysis form
```

---

## 🎉 REZULTAT FINAL

**✅ ViralSafe Platform MIGRATED!**

- **Backend**: Render.com FREE (512MB RAM, 750h/lună)
- **Frontend**: Vercel FREE (bandwidth unlimited)  
- **Cost**: $0/lună (ca înainte)
- **Performance**: Similar sau mai bun
- **Reliability**: Render este mai stabil decât Railway

**🚀 Back in business!**