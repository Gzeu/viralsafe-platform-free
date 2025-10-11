# 🚀 ViralSafe v3.1 Enhanced - Deployment Guide

**Complete deployment instructions for the world's most advanced open-source content safety analysis platform**

---

## 🎩 **Quick Deploy (5 Minutes)**

### **1. Get API Keys (Required)**

#### **🤖 Groq API (Primary AI - FREE)**
```bash
# Get free Groq API key (1M tokens/day)
1. Visit: https://console.groq.com/keys
2. Sign up with GitHub/Google
3. Create new API key
4. Copy: gsk_...
```

#### **💾 MongoDB Atlas (Storage - FREE)**
```bash
# Get free MongoDB Atlas (512MB)
1. Visit: https://www.mongodb.com/cloud/atlas/register
2. Create M0 cluster (free tier)
3. Add database user
4. Network access: 0.0.0.0/0
5. Copy connection string
```

#### **🛡️ VirusTotal API (Optional - FREE)**
```bash
# Get free VirusTotal API (1000 requests/day)
1. Visit: https://www.virustotal.com/gui/join-us
2. Verify email
3. Profile → API Key
4. Copy API key
```

### **2. Backend Deployment (Render.com)**

#### **Environment Variables:**
```bash
# REQUIRED
GROQ_API_KEY=gsk_your_groq_api_key_here
PYTHON_VERSION=3.11.0
PORT=10000

# RECOMMENDED
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
VIRUSTOTAL_API_KEY=your_virustotal_key
ENVIRONMENT=production

# OPTIONAL (Additional AI Providers)
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
```

#### **Render Settings:**
```bash
# Build Command:
pip install --upgrade pip && pip install -r requirements.txt

# Start Command:
uvicorn main:app --host 0.0.0.0 --port 10000

# Health Check Path:
/health

# Root Directory:
backend
```

### **3. Frontend Deployment (Vercel)**

#### **Environment Variables:**
```bash
# Production API URL
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

#### **Vercel Settings:**
```bash
# Framework: Next.js
# Root Directory: frontend
# Build Command: npm run build
# Output Directory: .next
```

---

## 📊 **Expected Results**

### **✅ Backend Health Check:**
```bash
curl https://your-backend.onrender.com/health

# Expected Response:
{
  "service": "ViralSafe Enhanced API",
  "version": "3.1.0",
  "status": "healthy",
  "features": {
    "ai_analysis": true,
    "advanced_scanning": true,
    "database_storage": true
  }
}
```

### **🤖 AI Analysis Test:**
```bash
curl -X POST "https://your-backend.onrender.com/api/advanced-scan" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'

# Expected Response:
{
  "url": "https://google.com",
  "trust_score": 95,
  "threat_level": 1,
  "ai_confidence": 98,
  "ai_insights": "Excellent security posture detected",
  "scan_time": 847,
  "ai_provider": "groq",
  "enhanced_mode": true
}
```

---

## 🔧 **Troubleshooting**

### **🚨 Common Issues:**

#### **1. "Import Error: No module named 'groq'"**
```bash
# Solution: Update requirements.txt deployed correctly
# Check Render build logs for pip install errors
# Ensure requirements.txt includes: groq==0.4.1
```

#### **2. "AI Analysis Failed"**
```bash
# Check GROQ_API_KEY is set correctly
# API key should start with 'gsk_'
# Verify key is active at console.groq.com
```

#### **3. "Database Connection Failed"**
```bash
# Verify MongoDB URI format:
# mongodb+srv://username:password@cluster.mongodb.net/dbname
# Check network access allows 0.0.0.0/0
# Test connection from MongoDB Compass
```

#### **4. "CORS Error from Frontend"**
```bash
# Ensure NEXT_PUBLIC_API_URL is set correctly
# Backend CORS includes frontend domain
# Check browser network tab for exact error
```

---

## 🏁 **Performance Optimization**

### **📨 Render.com Tips:**
```bash
# Prevent sleeping (free tier sleeps after 15min inactivity)
# Add uptime monitoring: https://uptimerobot.com
# Upgrade to Standard plan ($25/month) for no sleep

# Environment optimizations:
PYTHON_UNBUFFERED=1
UVICORN_WORKERS=1
UVICORN_WORKER_CONNECTIONS=1000
```

### **⚡ Performance Targets:**
- **Health Check**: <100ms
- **Basic Analysis**: <500ms
- **Advanced AI Scan**: <2s
- **Database Operations**: <50ms
- **Memory Usage**: <400MB (free tier: 512MB)

---

## 📈 **Monitoring & Analytics**

### **🔎 System Monitoring:**
```bash
# Health endpoint:
GET /health

# System status:
GET /api/system-status

# Analytics:
GET /api/analytics

# Service info:
GET /api/info
```

### **📊 Key Metrics:**
- **Uptime**: Target 99.9%
- **Response Time**: <2s avg
- **Error Rate**: <1%
- **AI Accuracy**: >95%
- **Cache Hit Ratio**: >70%

---

## 💰 **Cost Management**

### **🎆 Free Tier Limits:**

| Service | Free Limits | Monthly Cost |
|---------|-------------|-------------|
| **Render.com** | 750 hours, 512MB RAM | $0 |
| **Vercel** | 100GB bandwidth | $0 |
| **MongoDB Atlas** | 512MB storage | $0 |
| **Groq API** | 1M tokens/day | $0 |
| **VirusTotal** | 1000 requests/day | $0 |
| **Total** | **All features** | **$0/month** |

### **📈 Scaling Options:**
```bash
# When you outgrow free tiers:
# Render Standard: $25/month (no sleep, more resources)
# MongoDB M2: $9/month (2GB, dedicated)
# VirusTotal Premium: $180/month (15K requests/day)
# Groq Pay-as-you-go: $0.27/$1M tokens
```

---

## 🔒 **Security Configuration**

### **🌍 Environment Variables Security:**
```bash
# NEVER commit API keys to Git
# Use Render/Vercel environment variables
# Rotate keys periodically
# Monitor API usage for anomalies
```

### **🋡️ CORS Security:**
```bash
# Production CORS (automatically configured):
ALLOWED_ORIGINS = [
  "https://your-frontend.vercel.app",
  "https://your-domain.com"
]
```

---

## 🎨 **Custom Domain Setup**

### **🌐 Backend Custom Domain (Render):**
```bash
# Render Dashboard → Settings → Custom Domain
# Add CNAME: api.yourdomain.com → your-app.onrender.com
# SSL certificate automatically provisioned
```

### **🏠 Frontend Custom Domain (Vercel):**
```bash
# Vercel Dashboard → Settings → Domains
# Add domain: yourdomain.com
# Configure DNS: A record → 76.76.19.61
# SSL certificate automatically provisioned
```

---

## 📚 **API Documentation**

### **📄 Interactive Documentation:**
- **Swagger UI**: https://your-backend.onrender.com/docs
- **ReDoc**: https://your-backend.onrender.com/redoc
- **OpenAPI Schema**: https://your-backend.onrender.com/openapi.json

### **🐍 Python SDK Example:**
```python
import requests

# Advanced security scan
response = requests.post(
    "https://your-backend.onrender.com/api/advanced-scan",
    json={"url": "https://example.com", "deep_scan": True}
)

result = response.json()
print(f"Trust Score: {result['trust_score']}%")
print(f"AI Insights: {result['ai_insights']}")
```

### **⚗️ JavaScript/Node.js Example:**
```javascript
// Advanced security scan
const response = await fetch('https://your-backend.onrender.com/api/advanced-scan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://example.com', deep_scan: true })
});

const result = await response.json();
console.log(`Trust Score: ${result.trust_score}%`);
console.log(`AI Insights: ${result.ai_insights}`);
```

---

## 🎆 **Success Checklist**

### **✅ Backend Deployment:**
- [ ] Render service created and deployed
- [ ] Environment variables configured
- [ ] Health check returns 200 OK
- [ ] AI analysis endpoint working
- [ ] MongoDB connected (if configured)
- [ ] Logs show no errors

### **✅ Frontend Deployment:**
- [ ] Vercel deployment successful
- [ ] API URL environment variable set
- [ ] Advanced Security tab loading
- [ ] Scan functionality working
- [ ] Analytics displaying data

### **✅ Integration Testing:**
- [ ] End-to-end URL scan works
- [ ] AI analysis returns results
- [ ] Trust scores calculated correctly
- [ ] System status showing "healthy"
- [ ] Analytics tracking scans

---

## 🎉 **Congratulations!**

**Your ViralSafe v3.1 Enhanced platform is now live with:**

✅ **Multi-AI Security Analysis** (Groq + optionally Anthropic/OpenAI)  
✅ **9-Layer Advanced Scanning** (HTTP, Content, Security, DNS, SSL, etc.)  
✅ **Ultra-Fast Performance** (<2s comprehensive scans)  
✅ **Real-time Threat Intelligence** (URLhaus, OpenPhish, custom patterns)  
✅ **Smart Monitoring** (90%+ API savings vs traditional approaches)  
✅ **Advanced Analytics** (Real-time usage statistics)  
✅ **Enterprise Architecture** (Production-ready with comprehensive logging)  
✅ **Zero Monthly Cost** (100% free tier compliant)  

**🚀 Your platform is ready for enterprise production use!**

---

**📞 Need Help?**
- **GitHub Issues**: [Report bugs or request features](https://github.com/Gzeu/viralsafe-platform-free/issues)
- **GitHub Discussions**: [Community support](https://github.com/Gzeu/viralsafe-platform-free/discussions)
- **Documentation**: [Complete guides and API reference](https://github.com/Gzeu/viralsafe-platform-free)

**Made with ❤️ by George Pricop | ⭐ Star if you find this useful!**