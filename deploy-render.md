# 🚀 DEPLOY URGENT PE RENDER.COM - Railway Alternative

## ⚡ QUICK DEPLOY (2 minute)

### PASUL 1: Accesează Render
1. Du-te la **https://render.com**
2. Click **"Get Started for Free"**
3. **"Continue with GitHub"**
4. Autorizează Render să acceseze repo-urile

### PASUL 2: Creează Web Service
1. Click **"New +"** → **"Web Service"**
2. **"Connect a repository"** → Selectează **"viralsafe-platform-free"**
3. **Configurații:**
   ```
   Name: viralsafe-backend
   Root Directory: backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port 10000
   ```

### PASUL 3: Environment Variables
Adaugă în secțiunea "Environment":
```
PORT = 10000
ENVIRONMENT = production
CORS_ORIGINS = *
```

### PASUL 4: Deploy!
1. Click **"Create Web Service"**
2. Render va:
   - Clona repo-ul
   - Instala dependencies
   - Porni aplicația
   - Îți va da URL-ul: `https://viralsafe-backend-XXXX.onrender.com`

## 📋 URL-ul tău va fi:
**Backend**: `https://your-service-name.onrender.com`

### Test imediat:
```bash
curl https://your-service-name.onrender.com/health
```

## 🔄 Update Frontend URL

### În Vercel Dashboard:
1. Du-te la proiectul frontend
2. Settings → Environment Variables
3. **Update**:
   ```
   NEXT_PUBLIC_API_URL = https://your-service-name.onrender.com
   ```
4. **Redeploy** frontend

## ✅ GATA!
ViralSafe Platform rulează din nou pe Render.com FREE!

---

## 📊 Limite Render FREE:
- **512 MB RAM**
- **0.1 vCPU** 
- **750 ore/lună** (≈25 zile)
- **100 GB bandwidth**
- **SSL gratuit**
- **Se oprește după 15 min inactivitate**

## 🔧 Pro Tips:
- Render este **mai stabil** decât Railway era
- **Auto-deploy** când faci push pe GitHub
- **Logs în timp real** în dashboard
- **Custom domain** gratuit disponibil