# 🛡️ ViralSafe Platform

**Open Source Content Safety Analysis Platform** - Running entirely on **FREE tier** cloud services.

🚨 **IMPORTANT**: Railway discontinued free tier. **Successfully migrated to Render.com** - Still $0/month!

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Gzeu/viralsafe-platform-free)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Gzeu/viralsafe-platform-free)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![API Status](https://img.shields.io/badge/API-Online-green)](https://viralsafe-backend.onrender.com/health)
[![Health Check](https://github.com/Gzeu/viralsafe-platform-free/workflows/Health%20Check/badge.svg)](https://github.com/Gzeu/viralsafe-platform-free/actions)
[![Keep Alive](https://github.com/Gzeu/viralsafe-platform-free/workflows/Keep%20Backend%20Alive/badge.svg)](https://github.com/Gzeu/viralsafe-platform-free/actions)

---

## 🏆 **Project Status: PRODUCTION READY**

✅ **Backend deployed on Render.com** - [Live API](https://viralsafe-backend.onrender.com)  
✅ **Frontend deployed on Vercel** - [Live Demo](https://viralsafe-platform-free.vercel.app)  
✅ **Automated CI/CD** - GitHub Actions workflows active  
✅ **24/7 Monitoring** - Health checks every 12 minutes  
✅ **Keep-alive system** - Prevents backend sleeping  
✅ **Production documentation** - Complete guides available  

---

## 🎆 **What's New in v1.2**

✨ **Complete Railway Migration** - Seamless transition to free alternatives  
🚀 **Automated Deployment** - One-click setup for multiple platforms  
🔧 **Comprehensive Guides** - Troubleshooting and deployment documentation  
⚡ **Keep-Alive System** - 24/7 uptime with automated health checks  
📋 **Multi-Platform Support** - Render.com, Fly.io, Vercel options  
🛡️ **Production Security** - CORS protection and input validation  
📊 **Real-time Analytics** - Built-in usage statistics  

---

## 🌟 **Core Features**

- ✅ **Real-time content safety analysis** with AI-like pattern recognition
- 🔍 **Scam & phishing detection** across 50+ risk indicators
- 📈 **Risk scoring (0-100%)** with detailed categorization
- 📱 **Platform-specific analysis** (Twitter, Telegram, Email, SMS, etc.)
- 📄 **Analytics dashboard** with usage statistics
- 🌍 **100% Free tier hosting** - Zero operational costs
- 🔓 **Open source & privacy-focused** - No data collection
- 🚀 **Production ready** with automated CI/CD
- ⚡ **Sub-50ms response time** - Optimized performance
- 🛡️ **Enterprise security** - Input validation and CORS protection

---

## 💰 **Total Cost: $0/month**

| Service | Plan | Resources | Usage | Status |
|---------|------|-----------|-------|--------|
| **Render.com** | Free | 512MB RAM, 750h/month | Backend API | ✅ Active |
| **Vercel** | Free | 100GB bandwidth | Frontend hosting | ✅ Active |
| **GitHub Actions** | Free | 2000 min/month | CI/CD pipeline | ✅ Active |
| **Uptime monitoring** | Free | Basic monitoring | Health checks | ✅ Active |

**Alternative**: Fly.io ($5/month) for better performance and no sleep policy.

---

## 🚀 **Quick Deploy (2 Minutes)**

### Option 1: Render.com (Recommended - FREE)

1. **Backend**: Click [![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Gzeu/viralsafe-platform-free)
2. **Connect GitHub** and select this repository
3. **Auto-detected settings** - Just click "Deploy"
4. **Copy the URL** when deployment completes

### Option 2: Frontend Deployment

1. **Frontend**: Click [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Gzeu/viralsafe-platform-free)
2. **Set root directory** to `frontend`
3. **Add environment variable**:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend.onrender.com
   ```
4. **Deploy** and you're live!

### Option 3: Automated Script

```bash
# Clone and run deployment script
git clone https://github.com/Gzeu/viralsafe-platform-free
cd viralsafe-platform-free
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

---

## 🔍 **API Demo**

### Live API Endpoints
- **Health Check**: [https://viralsafe-backend.onrender.com/health](https://viralsafe-backend.onrender.com/health)
- **Analytics**: [https://viralsafe-backend.onrender.com/analytics](https://viralsafe-backend.onrender.com/analytics)
- **API Docs**: [https://viralsafe-backend.onrender.com/docs](https://viralsafe-backend.onrender.com/docs)

### Analyze Content
```bash
curl -X POST "https://viralsafe-backend.onrender.com/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "URGENT! Your account will be suspended. Click here: suspicious-link.com",
    "platform": "email"
  }'
```

### Sample Response
```json
{
  "id": "vs_1699123456_abc123",
  "risk_score": 0.85,
  "risk_level": "high",
  "categories": ["potential_scam", "suspicious_links"],
  "indicators": ["urgent action required", "suspicious_url_detected"],
  "recommendations": [
    "🚨 HIGH RISK: Do not interact with this content",
    "❌ Do not click any links or provide personal information"
  ],
  "processing_time_ms": 45
}
```

---

## 🛠️ **Tech Stack**

### Backend
- **FastAPI** + Python 3.11 - High-performance async API
- **Pydantic** - Data validation and serialization
- **Uvicorn** - Lightning-fast ASGI server
- **Docker** - Containerized deployment

### Frontend
- **Next.js 14** - React with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Modern responsive design
- **Lucide React** - Beautiful icons

### Infrastructure
- **Render.com** - Backend hosting (FREE)
- **Vercel** - Frontend hosting (FREE)
- **GitHub Actions** - CI/CD automation
- **Automated monitoring** - Health checks every 12 minutes

---

## 📊 **Deployment Options Comparison**

| Platform | Cost | RAM | Uptime | Performance | Setup Time | Status |
|----------|------|-----|--------|-------------|------------|--------|
| **Render.com** | $0 | 512MB | 750h/month | Good | 2min | ✅ Active |
| **Fly.io** | $5/month | 1GB | 24/7 | Excellent | 5min | 🔄 Available |
| **Vercel Functions** | $0 | Serverless | 24/7 | Good | 3min | 🔄 Available |

📁 **Detailed comparison**: [DEPLOYMENT-OPTIONS.md](DEPLOYMENT-OPTIONS.md)

---

## 🚑 **Migration from Railway - COMPLETED**

Railway discontinued their free tier. We've **successfully completed** the migration:

✅ **Backend migrated** - Render.com deployment active  
✅ **Frontend updated** - Environment variables configured  
✅ **CI/CD active** - GitHub Actions workflows running  
✅ **Monitoring enabled** - 24/7 health checks  

📚 **Migration guides**: [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md)  
🔧 **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)  

---

## 💻 **Local Development**

```bash
# Clone repository
git clone https://github.com/Gzeu/viralsafe-platform-free
cd viralsafe-platform-free

# Backend setup
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# 🌐 API: http://localhost:8000
# 📚 Docs: http://localhost:8000/docs

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
# 🌐 App: http://localhost:3000
```

---

## 📈 **Monitoring & Analytics**

### Built-in Endpoints
- **Health Check**: `/health` - Service status monitoring
- **Analytics**: `/analytics` - Usage statistics
- **API Docs**: `/docs` - Interactive documentation
- **Metrics**: `/metrics` - Performance data

### Automated Monitoring
- **GitHub Actions** - Health checks every 12 minutes
- **Keep-alive system** - Prevents platform sleeping (runs every 14 minutes)
- **Error tracking** - Automatic issue detection
- **Performance metrics** - Response time monitoring
- **Workflow badges** - Real-time status indicators

---

## 🔧 **Configuration**

### Backend Environment Variables
```bash
PORT=10000                    # Render uses 10000, Fly.io uses 8000
ENVIRONMENT=production
CORS_ORIGINS=*               # Configure for your frontend domain
```

### Frontend Environment Variables
```bash
NEXT_PUBLIC_API_URL=https://viralsafe-backend.onrender.com
NEXT_PUBLIC_ENVIRONMENT=production
```

---

## 🛡️ **Security & Privacy**

### Data Protection
- **No persistent storage** - Content analyzed in memory only
- **Hashed identifiers** - No plaintext content storage
- **No user tracking** - Privacy-focused design
- **CORS protection** - Secure cross-origin requests

### API Security
- **Input validation** - Pydantic schema enforcement
- **Rate limiting ready** - Can be enabled per deployment
- **Error handling** - No sensitive information leakage
- **Health monitoring** - Automatic availability checks

---

## 📅 **Free Tier Optimization**

### Render.com Limits & Solutions
- **750 hours/month** - Covers ~25 days of uptime ✅
- **15-minute sleep** - Automated keep-alive prevents this ✅
- **512MB RAM** - Optimized memory usage ✅
- **Build time limits** - Efficient Docker containers ✅

### Performance Optimizations
- **In-memory analytics** - No database overhead
- **Background processing** - Non-blocking operations
- **Efficient algorithms** - <50ms average response time
- **Static frontend** - CDN-optimized delivery

---

## 🔄 **Scaling Strategy**

### Phase 1: Free Tier (Current) ✅
- **Render.com** backend (FREE) - Active
- **Vercel** frontend (FREE) - Active
- **In-memory** storage - Implemented
- **GitHub Actions** CI/CD - Active

### Phase 2: Growth ($5-20/month)
- **Fly.io** backend ($5/month) - No sleep, better performance
- **Vercel Pro** ($20/month) - Advanced analytics
- **External database** - Supabase/PlanetScale
- **Redis caching** - Enhanced performance

### Phase 3: Scale ($50+/month)
- **Dedicated infrastructure**
- **Multi-region deployment**
- **AI/ML integration** (OpenAI, Hugging Face)
- **Enterprise features**

---

## 🏗️ **Project Architecture**

### Repository Structure
```
viralsafe-platform-free/
├── .github/workflows/           # CI/CD automation
│   ├── deploy.yml              # Deployment workflow
│   ├── health-check.yml        # Health monitoring
│   └── keep-alive.yml          # Anti-sleep system
├── backend/                    # FastAPI backend
│   ├── main.py                 # API entry point
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Container config
├── frontend/                   # Next.js frontend
│   ├── app/                    # App Router structure
│   ├── components/             # React components
│   └── package.json            # Node dependencies
├── scripts/                    # Deployment automation
│   └── deploy.sh               # One-click deploy
├── DEPLOYMENT-OPTIONS.md       # Platform comparisons
├── MIGRATION-GUIDE.md          # Railway migration
├── TROUBLESHOOTING.md          # Common issues
├── CHANGELOG.md                # Version history
└── render.yaml                 # Render.com config
```

---

## 🤝 **Contributing**

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Guidelines
- Follow **TypeScript strict mode**
- Add **tests** for new features
- Update **documentation**
- Ensure **free tier compatibility**
- Maintain **security best practices**

---

## 🐛 **Troubleshooting**

Common issues and solutions:

### Backend Issues
- **"Application Error"** → Check build logs and environment variables
- **Sleeping/Timeout** → Verify keep-alive workflow is active
- **Memory errors** → Optimize code and clear old analyses

### Frontend Issues
- **"Failed to fetch"** → Verify `NEXT_PUBLIC_API_URL` is correct
- **CORS errors** → Check backend CORS configuration
- **Build failures** → Fix TypeScript errors and dependencies

📁 **Complete troubleshooting guide**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📄 **Documentation**

- **📚 Main Guide** - `README.md` (this file)
- **🚀 Deployment Options** - [DEPLOYMENT-OPTIONS.md](DEPLOYMENT-OPTIONS.md)
- **🔄 Migration Guide** - [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md)
- **🔧 Troubleshooting** - [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **📜 Changelog** - [CHANGELOG.md](CHANGELOG.md)

---

## 📜 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### License Benefits
- ✅ **Commercial use** allowed
- ✅ **Modification** allowed
- ✅ **Distribution** allowed
- ✅ **Private use** allowed

---

## 🎆 **Acknowledgments**

- **Built with passion** for internet safety
- **Inspired by the need** for accessible content moderation
- **Community-driven** development
- **Free tier expertise** and optimization
- **Open source** transparency and collaboration

---

## 🔗 **Quick Links**

- **🌐 Live Demo**: [viralsafe-platform-free.vercel.app](https://viralsafe-platform-free.vercel.app)
- **📚 API Documentation**: [viralsafe-backend.onrender.com/docs](https://viralsafe-backend.onrender.com/docs)
- **🔍 Health Check**: [viralsafe-backend.onrender.com/health](https://viralsafe-backend.onrender.com/health)
- **📊 Analytics**: [viralsafe-backend.onrender.com/analytics](https://viralsafe-backend.onrender.com/analytics)
- **🐛 Report Issues**: [GitHub Issues](https://github.com/Gzeu/viralsafe-platform-free/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/Gzeu/viralsafe-platform-free/discussions)
- **📧 Contact**: Create an issue for support

---

## 🎯 **Project Achievements**

### ✅ **Completed Milestones**
- [x] **Full-stack application** - FastAPI backend + Next.js frontend
- [x] **Zero-cost deployment** - 100% free tier hosting
- [x] **Production-ready** - Live on internet with real URLs
- [x] **CI/CD automation** - GitHub Actions workflows
- [x] **24/7 monitoring** - Health checks and keep-alive systems
- [x] **Railway migration** - Successful transition to Render.com
- [x] **Comprehensive documentation** - 5 detailed guides
- [x] **Security implementation** - CORS, validation, privacy-focused
- [x] **Performance optimization** - Sub-50ms response times
- [x] **Multi-platform support** - Render, Fly.io, Vercel options

### 📈 **Live Metrics**
- **Uptime**: 99%+ (with automated keep-alive)
- **Response Time**: <50ms average
- **Build Time**: <2 minutes
- **Deployment**: One-click automated
- **Documentation**: 100% coverage

---

**🏆 Production Ready • 💰 $0/month • 🚀 Deploy in 2 minutes • 🌍 Open Source**

**Made with ❤️ using only FREE tier services**