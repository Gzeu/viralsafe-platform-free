# 🛡️ ViralSafe Platform

Open source content safety analysis platform running entirely on **FREE tier** cloud services.

[![Deploy Backend](https://img.shields.io/badge/Deploy-Railway-purple)](https://railway.app)
[![Deploy Frontend](https://img.shields.io/badge/Deploy-Vercel-black)](https://vercel.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![API Status](https://img.shields.io/badge/API-Online-green)]()

## 🌟 Features

- ✅ **Real-time content safety analysis**
- 🔍 **Scam & phishing detection**
- 📊 **Risk scoring (0-100%)**
- 🤖 **AI-like pattern recognition**
- 📱 **Platform-specific analysis** (Twitter, Telegram, etc)
- 📈 **Analytics dashboard**
- 🆓 **100% Free tier hosting**
- 🌍 **Open source & community driven**

## 💰 Total Cost: $0/month

| Service | Free Tier Limits | Usage |
|---------|------------------|--------|
| **Railway** | 500h/month, 1GB RAM | Backend API |
| **Vercel** | 100GB bandwidth | Frontend hosting |
| **GitHub Actions** | 2000 min/month | CI/CD pipeline |
| **Uptime monitoring** | Basic monitoring | Health checks |

## 🚀 Quick Deploy (5 minutes)

### 1. Deploy Backend to Railway FREE

1. Fork this repo
2. Go to [https://railway.app](https://railway.app/)
3. Login with GitHub
4. Click "Deploy from GitHub repo"
5. Select your fork → backend folder
6. Railway auto-detects Python and deploys!

### 2. Deploy Frontend to Vercel FREE

1. Go to [https://vercel.com](https://vercel.com/)
2. Login with GitHub
3. Click "Import project"
4. Select your fork
5. Set root directory to "frontend"
6. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL = https://your-railway-app.railway.app/
   ```
7. Deploy!

### 3. Local Development

```bash
# Clone repo
git clone https://github.com/Gzeu/viralsafe-platform-free
cd viralsafe-platform-free

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API running at http://localhost:8000/

# Frontend (new terminal)
cd frontend
npm install
npm run dev
# Frontend at http://localhost:3000/
```

## 📊 API Usage Examples

### Analyze Content

```bash
curl -X POST "https://your-api.railway.app/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "URGENT! Your account will be suspended. Click here to verify: suspicious-link.com",
    "platform": "email"
  }'
```

### Response

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

## 🛠️ Tech Stack

- **Backend**: FastAPI + Python 3.11
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Hosting**: Railway (API) + Vercel (Frontend)
- **CI/CD**: GitHub Actions
- **Monitoring**: Built-in health checks

## 📈 Monitoring & Analytics

- **Health endpoint**: `/health`
- **Analytics**: `/analytics`
- **API docs**: `/docs`
- **Uptime monitoring**: GitHub Actions every 15min

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```
PORT=8000
ENVIRONMENT=production
CORS_ORIGINS=*
```

**Frontend (.env.local):**
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/
NEXT_PUBLIC_ENVIRONMENT=production
```

## 🚦 Free Tier Limits & Optimizations

### Railway Backend Limits:
- **500 hours/month** (≈16h/day) 
- **1GB RAM, 1 vCPU**
- **Sleeps after 15min inactivity**

**Optimizations:**
- In-memory storage (no DB costs)
- Efficient algorithms
- Background task processing
- Health check endpoints for uptime

### Vercel Frontend Limits:
- **100GB bandwidth/month**
- **1000 serverless function executions**
- **Static hosting** (fast CDN)

## 📊 Scaling Strategy

### When you outgrow free tier:

1. **Backend scaling**: 
   - Railway Pro ($5/month)
   - Add Redis for caching
   - External database (Supabase/PlanetScale)

2. **Frontend scaling**:
   - Vercel Pro ($20/month) 
   - Better analytics
   - Edge functions

3. **AI Enhancement**:
   - OpenAI API integration
   - Hugging Face inference
   - Custom ML models

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Development Guidelines

- Follow TypeScript strict mode
- Add tests for new features
- Update documentation
- Ensure free tier compatibility

## 🐛 Common Issues & Fixes

### Backend Issues:
- **Railway sleeping**: Add health check pings
- **Memory limits**: Optimize data structures
- **Cold starts**: Use keep-alive mechanisms

### Frontend Issues:
- **API timeout**: Add retry logic
- **Build fails**: Check TypeScript errors
- **ENV vars**: Verify NEXT_PUBLIC_ prefix

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⭐ Star History

Support this project by giving it a star! 

## 🙏 Acknowledgments

- Built with love for internet safety
- Inspired by the need for accessible content moderation
- Community-driven development
- Free tier optimization expertise

---

### 🔗 Links

- **🌐 Live Demo**: [viralsafe.vercel.app](https://viralsafe.vercel.app)
- **📚 API Docs**: [api.viralsafe.app/docs](https://api.viralsafe.app/docs)
- **🐛 Report Bug**: [GitHub Issues](https://github.com/Gzeu/viralsafe-platform-free/issues)
- **💡 Request Feature**: [GitHub Discussions](https://github.com/Gzeu/viralsafe-platform-free/discussions)

**Made with ❤️ using only FREE tier services**