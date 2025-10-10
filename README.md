# 🛡️ ViralSafe Platform

**Advanced Content Safety Analysis Platform** - Production-ready with MongoDB Atlas & VirusTotal integration.

🎉 **ENTERPRISE-GRADE FEATURES** - MongoDB Atlas + VirusTotal API + Real-time Analytics

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Gzeu/viralsafe-platform-free)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Gzeu/viralsafe-platform-free)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![API Status](https://img.shields.io/badge/API-Online-green)](https://viralsafe-platform-free-api.onrender.com/health)
[![Frontend Status](https://img.shields.io/badge/Frontend-Live-blue)](https://viralsafe-platform-free.vercel.app)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)](https://www.mongodb.com/atlas)
[![VirusTotal](https://img.shields.io/badge/VirusTotal-API-orange)](https://www.virustotal.com/)
[![CI/CD](https://github.com/Gzeu/viralsafe-platform-free/workflows/ViralSafe%20Platform%20CI/CD/badge.svg)](https://github.com/Gzeu/viralsafe-platform-free/actions)

---

## 🚀 **LATEST: v2.0 - Production Enterprise Edition**

🎆 **NEW: MongoDB Atlas Integration** - Persistent storage and analytics  
🛡️ **NEW: VirusTotal API** - URL scanning and malware detection  
📊 **NEW: Real-time Analytics Dashboard** - Advanced metrics and monitoring  
⚡ **NEW: System Health Monitoring** - Live service status tracking  
🔧 **NEW: GitHub Secrets Integration** - Secure environment management  
🎨 **NEW: Enhanced Frontend** - 3-tab interface with advanced features  

---

## 🏆 **Project Status: ✅ ENTERPRISE PRODUCTION READY**

✅ **Backend**: FastAPI + MongoDB Atlas + VirusTotal - [Live API](https://viralsafe-platform-free-api.onrender.com)  
✅ **Frontend**: Next.js with advanced dashboard - [Live Demo](https://viralsafe-platform-free.vercel.app)  
✅ **Database**: MongoDB Atlas cloud database - Persistent storage  
✅ **Security API**: VirusTotal integration - URL scanning & analysis  
✅ **CI/CD**: GitHub Actions with comprehensive testing  
✅ **Monitoring**: 24/7 health checks and system monitoring  
✅ **Documentation**: Complete enterprise setup guides  

---

## 🌐 **Live Deployments**

### 🚀 **Production Deployment**
- **🎯 Frontend**: [https://viralsafe-platform-free.vercel.app](https://viralsafe-platform-free.vercel.app)
- **⚡ Backend API**: [https://viralsafe-platform-free-api.onrender.com](https://viralsafe-platform-free-api.onrender.com)
- **📚 API Documentation**: [/docs](https://viralsafe-platform-free-api.onrender.com/docs)
- **🔍 Health Monitoring**: [/health](https://viralsafe-platform-free-api.onrender.com/health)
- **📊 Analytics Dashboard**: [/analytics](https://viralsafe-platform-free-api.onrender.com/analytics)

### 🎨 **Project Resources**
- **📁 Repository**: [GitHub](https://github.com/Gzeu/viralsafe-platform-free)
- **🏗️ CI/CD Pipeline**: [GitHub Actions](https://github.com/Gzeu/viralsafe-platform-free/actions)
- **🔐 Secrets Management**: [GitHub Secrets](https://github.com/Gzeu/viralsafe-platform-free/settings/secrets/actions)

---

## 🌟 **Enterprise Features**

### 🛡️ **Advanced Content Analysis**
- ✅ **AI-powered risk assessment** with 50+ threat indicators
- 🔍 **Multi-category detection**: Scams, phishing, misinformation, malware
- 📊 **Risk scoring (0-100%)** with detailed explanations
- 🏷️ **Platform-specific analysis** (Twitter, Facebook, Telegram, Email, SMS, etc.)
- 🌐 **URL scanning** with VirusTotal API integration
- ⚡ **Real-time processing** with <50ms response times

### 💾 **Data & Analytics**
- 🏗️ **MongoDB Atlas** - Cloud database with persistent storage
- 📈 **Real-time analytics** - Usage statistics and trend analysis
- 🎯 **Risk distribution tracking** - High/Medium/Low risk categorization
- 📱 **Platform usage statistics** - Detailed breakdown by source
- 🔄 **Historical data** - Analysis history and patterns
- 📊 **Live dashboard** - Interactive analytics interface

### 🔒 **Security & Integrations**
- 🛡️ **VirusTotal API** - URL scanning and malware detection
- 🔐 **GitHub Secrets** - Secure environment variable management
- 🌍 **CORS protection** - Secure cross-origin requests
- ✅ **Input validation** - Comprehensive data sanitization
- 🚫 **No data collection** - Privacy-focused design
- 🔄 **Rate limiting ready** - API protection mechanisms

### 📊 **System Monitoring**
- ⚡ **Real-time health checks** - Service status monitoring
- 📈 **Performance metrics** - Response times and system load
- 🔄 **Auto-refresh dashboards** - Live status updates
- 📱 **Service dependencies** - MongoDB & VirusTotal status
- ⏰ **Uptime tracking** - 24/7 monitoring
- 🚨 **Error detection** - Automated issue reporting

---

## 💰 **Cost Structure**

| Service | Plan | Resources | Usage | Monthly Cost |
|---------|------|-----------|-------|-------------|
| **Render.com** | Free | 512MB RAM, 750h/month | Backend API | $0 |
| **Vercel** | Free | 100GB bandwidth | Frontend | $0 |
| **MongoDB Atlas** | Free M0 | 512MB storage | Database | $0 |
| **VirusTotal** | Free API | 1000 requests/day | URL scanning | $0 |
| **GitHub** | Free | 2000 min/month | CI/CD & secrets | $0 |

**🎯 Total Monthly Cost: $0** (Free tier limits sufficient for development/testing)

**📈 Production Scale Options:**
- **MongoDB Atlas M2**: $9/month (2GB RAM, shared clusters)
- **VirusTotal Premium**: $180/month (15,000 requests/day)
- **Render Standard**: $25/month (2GB RAM, no sleep)

---

## 🚀 **Quick Deploy (5 Minutes)**

### Step 1: MongoDB Atlas Setup
1. **Create account**: [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. **Create cluster**: Choose M0 Free tier
3. **Network access**: Add `0.0.0.0/0` (allow all IPs)
4. **Database user**: Create username/password
5. **Get connection string**: Copy MongoDB URI

### Step 2: VirusTotal API Key
1. **Create account**: [VirusTotal](https://www.virustotal.com/gui/join-us)
2. **Get API key**: Profile → API Key
3. **Copy key**: Save for environment variables

### Step 3: GitHub Secrets Configuration
1. Go to **Repository Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   ```
   MONGODB_URI = mongodb+srv://username:password@cluster.mongodb.net/
   MONGODB_DB_NAME = viralsafe
   VIRUSTOTAL_API_KEY = your_virustotal_api_key
   HASH_SALT = your_secure_random_string
   ENVIRONMENT = production
   ```

### Step 4: Deploy Backend (Render.com)
1. **Connect GitHub**: [Render.com](https://render.com) → New → Web Service
2. **Repository**: Select `viralsafe-platform-free`
3. **Settings**:
   ```
   Name: viralsafe-platform-free-api
   Environment: Python 3.11
   Root Directory: backend
   Build Command: pip install -r requirements.txt
   Start Command: python main.py
   ```
4. **Environment Variables**: Same as GitHub Secrets
5. **Deploy**: Click "Create Web Service"

### Step 5: Deploy Frontend (Vercel)
1. **Import project**: [Vercel](https://vercel.com/new)
2. **Repository**: Select `viralsafe-platform-free`
3. **Framework**: Next.js
4. **Root Directory**: frontend
5. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend.onrender.com
   ```
6. **Deploy**: Click "Deploy"

---

## 🔍 **API Demo & Testing**

### Live API Endpoints
```bash
# Health Check
curl https://viralsafe-platform-free-api.onrender.com/health

# System Analytics
curl https://viralsafe-platform-free-api.onrender.com/analytics

# Content Analysis
curl -X POST "https://viralsafe-platform-free-api.onrender.com/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "URGENT! Your account will be suspended. Click here to verify: suspicious-link.com",
    "platform": "email",
    "url": "https://suspicious-link.com",
    "check_urls": true
  }'
```

### Enhanced Response with VirusTotal
```json
{
  "id": "vs_1699123456_abc123",
  "content_hash": "a1b2c3d4e5f6",
  "risk_score": 0.89,
  "risk_level": "high",
  "categories": ["potential_scam", "malicious_url", "phishing"],
  "indicators": [
    "urgent action required",
    "virustotal_malicious_detections: 12",
    "suspicious_url_detected"
  ],
  "recommendations": [
    "🚨 HIGH RISK: Do not interact with this content",
    "❌ Do not click any links or provide personal information",
    "📢 Consider reporting this content to the platform"
  ],
  "platform": "email",
  "timestamp": "2025-10-10T19:00:00Z",
  "processing_time_ms": 342,
  "virustotal_report": {
    "url": "https://suspicious-link.com",
    "risk_score": 0.92,
    "total_engines": 68,
    "malicious": 12,
    "suspicious": 8,
    "clean": 48,
    "scan_date": "2025-10-10T18:30:00Z",
    "reputation": -15
  }
}
```

---

**🚀 Enterprise-Grade • 💾 MongoDB Atlas • 🛡️ VirusTotal API • 📊 Real-time Analytics**

**✨ Production Ready with Advanced Security & Monitoring ✨**

**🏆 Built with enterprise patterns using FREE tier services 🏆**

---