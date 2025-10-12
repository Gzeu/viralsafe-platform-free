# 🛡️ ViralSafe Platform - Free Tier

> AI-powered content safety analysis with scam detection, phishing analysis & risk scoring. Running entirely on **FREE tier** (Vercel + MongoDB Atlas). Zero monthly costs!

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/Gzeu/viralsafe-platform-free.git
cd viralsafe-platform-free
npm install
```

### 2. Environment Setup
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
MONGODB_URI=your_mongodb_atlas_connection_string
VIRUSTOTAL_API_KEY=your_virustotal_api_key
RATELIMIT_MAX=60
RATELIMIT_WINDOW_MS=60000
```

### 3. Run Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) 🎉

## 🌐 Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Gzeu/viralsafe-platform-free)

### Environment Variables in Vercel:
- `MONGODB_URI` - MongoDB Atlas connection string
- `VIRUSTOTAL_API_KEY` - VirusTotal API key
- `RATELIMIT_MAX` - Rate limit per window (default: 60)
- `RATELIMIT_WINDOW_MS` - Rate limit window in ms (default: 60000)

## 📊 API Endpoints

- `POST /api/analyze` - Analyze text/URL with AI risk scoring
- `POST /api/scan` - Scan URL with VirusTotal
- `GET /api/analytics` - Usage statistics
- `GET /api/health` - System health check

## 🎨 Features

- ✅ **Next.js 14** with App Router
- ✅ **AI Analysis** with fallback heuristics
- ✅ **VirusTotal Integration** with polling
- ✅ **MongoDB Atlas** for data persistence
- ✅ **Rate Limiting** per IP
- ✅ **Batch Processing** for multiple URLs
- ✅ **Export** to CSV/JSON/PDF
- ✅ **Dark Mode** & responsive design
- ✅ **TypeScript** & Zod validation

## 📝 Testing

```bash
# Test analyze endpoint
curl -X POST http://localhost:3000/api/analyze \\
  -H "Content-Type: application/json" \\
  -d '{"inputType":"text","content":"free crypto airdrop"}'

# Test scan endpoint  
curl -X POST http://localhost:3000/api/scan \\
  -H "Content-Type: application/json" \\
  -d '{"url":"https://example.com"}'
```

## 🛠️ Development

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

## 📊 Architecture

```
🏠 Next.js App
├── 🎨 Frontend (React + Tailwind)
│   ├── Analysis Form
│   ├── Batch Uploader
│   ├── Export Tools
│   └── Analytics Dashboard
│
├── 🏭 API Routes (/api/*)
│   ├── /analyze - AI + Risk Scoring
│   ├── /scan - VirusTotal Integration
│   ├── /analytics - Usage Stats
│   └── /health - System Check
│
├── 📦 Database (MongoDB Atlas)
│   ├── Analysis Collection
│   └── Scan Collection
│
└── 🔌 External APIs
    ├── VirusTotal API
    └── AI Providers (OpenAI/Groq/Gemini)
```

## 🔒 Security

- Rate limiting per IP address
- Input validation with Zod schemas
- Environment variable protection
- CORS configured for production
- SQL injection protection via Mongoose

## 🎆 Free Tier Stack

- **Frontend**: Vercel (Free)
- **Backend**: Vercel Serverless Functions (Free)
- **Database**: MongoDB Atlas (512MB Free)
- **AI**: Provider free tiers + heuristic fallback
- **CDN**: Vercel Edge Network (Free)

**Total Monthly Cost: $0** 🎉

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Support

If you find this project helpful, please give it a ⭐ star!

---

**Built with ❤️ by [Gzeu](https://github.com/Gzeu)**