# 🔧 ViralSafe Platform - Troubleshooting Guide

## 🎯 Quick Issue Resolution

### 🚨 Platform Currently Down?
**Immediate Checks:**
```bash
# 1. Check backend health
curl https://your-backend-url.onrender.com/health

# 2. Check frontend
curl https://your-frontend.vercel.app

# 3. Check if API is responding
curl -X POST "https://your-backend-url.onrender.com/analyze" \
  -H "Content-Type: application/json" \
  -d '{"content":"test","platform":"general"}'
```

---

## 💻 Backend Issues

### 🚫 Issue: "Application Error" on Render.com

**Symptoms:**
- Page shows "Application Error"
- 502 Bad Gateway
- Service unavailable

**Solutions:**

1. **Check Build Logs:**
   ```bash
   # Go to Render Dashboard > Your Service > Logs
   # Look for build errors
   ```

2. **Common Build Fixes:**
   ```bash
   # requirements.txt issues
   pip install -r requirements.txt  # Test locally first
   
   # Port configuration
   # Ensure main.py has:
   port = int(os.environ.get("PORT", 10000))
   ```

3. **Environment Variables:**
   ```
   PORT=10000
   ENVIRONMENT=production
   CORS_ORIGINS=*
   ```

### 😴 Issue: Backend Sleeping Too Often

**Symptoms:**
- First request takes 20+ seconds
- API unresponsive after inactivity
- Cold start delays

**Solutions:**

1. **Health Check Automation:**
   ```yaml
   # .github/workflows/keep-alive.yml
   name: Keep Backend Alive
   on:
     schedule:
       - cron: '*/14 * * * *'  # Every 14 minutes
   jobs:
     ping:
       runs-on: ubuntu-latest
       steps:
         - name: Ping Backend
           run: |
             curl -f "${{ secrets.BACKEND_URL }}/health" || echo "Ping failed"
   ```

2. **UptimeRobot Setup:**
   - Go to [uptimerobot.com](https://uptimerobot.com)
   - Add HTTP monitor
   - URL: `https://your-backend.onrender.com/health`
   - Interval: 5 minutes
   - Free account allows 50 monitors

### 📊 Issue: High Memory Usage

**Symptoms:**
- Build fails with memory errors
- App crashes randomly
- "Memory limit exceeded"

**Solutions:**

1. **Optimize Dependencies:**
   ```python
   # Remove unused imports
   # Use lighter alternatives
   # requirements.txt - keep only essentials:
   fastapi==0.104.1
   uvicorn[standard]==0.24.0
   pydantic==2.5.0
   ```

2. **Memory Management:**
   ```python
   # In main.py - limit in-memory storage
   MAX_ANALYSES = 1000  # Limit stored analyses
   
   def cleanup_old_analyses():
       if len(analysis_store) > MAX_ANALYSES:
           # Remove oldest 20%
           old_keys = list(analysis_store.keys())[:200]
           for key in old_keys:
               del analysis_store[key]
   ```

### ⚡ Issue: Slow API Response

**Symptoms:**
- API takes >5 seconds to respond
- Timeout errors
- Poor user experience

**Solutions:**

1. **Optimize Analysis Function:**
   ```python
   # Cache compiled patterns
   import re
   HIGH_RISK_PATTERNS = [re.compile(pattern) for pattern in high_risk_patterns]
   
   def analyze_content_safety_optimized(content: str, platform: str):
       # Use compiled regex for faster matching
       content_lower = content.lower()
       
       # Early return for empty content
       if not content_lower.strip():
           return default_safe_result()
   ```

2. **Background Processing:**
   ```python
   # Move heavy analytics to background
   @app.post("/analyze")
   async def analyze_content(request: ContentRequest, background_tasks: BackgroundTasks):
       # Quick analysis first
       result = quick_analyze(request.content)
       
       # Heavy processing in background
       background_tasks.add_task(detailed_analysis, request.content)
       
       return result
   ```

---

## 🎨 Frontend Issues

### 🚫 Issue: "Failed to Fetch" Error

**Symptoms:**
- Frontend can't connect to backend
- CORS errors in browser console
- Network errors

**Solutions:**

1. **Check Environment Variables:**
   ```bash
   # Vercel Dashboard > Project > Settings > Environment Variables
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   
   # Make sure there's no trailing slash!
   # WRONG: https://your-backend.onrender.com/
   # RIGHT: https://your-backend.onrender.com
   ```

2. **CORS Configuration:**
   ```python
   # In backend/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend.vercel.app"],  # Specific domain
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Test API Connection:**
   ```javascript
   // In browser console
   fetch('https://your-backend.onrender.com/health')
     .then(r => r.json())
     .then(console.log)
     .catch(console.error)
   ```

### 📱 Issue: Mobile/Responsive Problems

**Symptoms:**
- UI broken on mobile
- Text too small
- Buttons not clickable

**Solutions:**

1. **Check Tailwind Config:**
   ```javascript
   // tailwind.config.js
   module.exports = {
     content: ['./app/**/*.{js,ts,jsx,tsx}'],  // Correct paths
     theme: {
       extend: {
         screens: {
           'xs': '475px',  // Add extra small breakpoint
         }
       }
     }
   }
   ```

2. **Mobile-First CSS:**
   ```jsx
   // Use responsive classes
   <div className="w-full max-w-sm mx-auto md:max-w-2xl lg:max-w-4xl">
   <button className="w-full py-2 px-4 text-sm md:text-base lg:text-lg">
   ```

### 📄 Issue: Build Failures

**Symptoms:**
- Vercel build fails
- TypeScript errors
- Missing dependencies

**Solutions:**

1. **Fix TypeScript Errors:**
   ```typescript
   // Add proper types
   interface AnalysisResult {
     id: string;
     risk_score: number;
     // ... other properties
   }
   
   const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
   ```

2. **Dependency Issues:**
   ```bash
   # Clear node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   
   # Or use exact versions
   npm install react@18.2.0 react-dom@18.2.0
   ```

---

## 🔄 CI/CD Issues

### 🚫 Issue: GitHub Actions Failing

**Symptoms:**
- Build/deploy actions fail
- Tests not running
- Health checks failing

**Solutions:**

1. **Check Secrets:**
   ```bash
   # GitHub Repo > Settings > Secrets and Variables > Actions
   BACKEND_URL=https://your-backend.onrender.com
   FRONTEND_URL=https://your-frontend.vercel.app
   RENDER_DEPLOY_HOOK=https://api.render.com/deploy/...
   ```

2. **Fix Action Permissions:**
   ```yaml
   # .github/workflows/health-check.yml
   permissions:
     contents: read
     actions: read
   ```

3. **Debug Actions:**
   ```yaml
   - name: Debug Environment
     run: |
       echo "Backend URL: ${{ secrets.BACKEND_URL }}"
       curl -v "${{ secrets.BACKEND_URL }}/health"
   ```

---

## 🔍 Monitoring & Debugging

### 📏 Enable Detailed Logging

```python
# Add to backend/main.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/analyze")
async def analyze_content(request: ContentRequest):
    logger.info(f"Analyzing content from {request.platform}")
    try:
        result = analyze_content_safety(request.content, request.platform)
        logger.info(f"Analysis completed in {result['processing_time_ms']}ms")
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")
```

### 📊 Performance Monitoring

```python
# Add metrics endpoint
@app.get("/metrics")
def get_metrics():
    import psutil
    import time
    
    return {
        "memory_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent(),
        "disk_usage": psutil.disk_usage('/').percent,
        "analyses_count": len(analysis_store),
        "uptime": time.time() - start_time
    }
```

### 🚨 Health Check Enhancement

```python
@app.get("/health")
def enhanced_health_check():
    try:
        # Test database connection if using one
        # Test external services
        # Check memory usage
        
        memory_percent = psutil.virtual_memory().percent
        
        status = "healthy"
        if memory_percent > 90:
            status = "warning"
        if memory_percent > 95:
            status = "critical"
            
        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "memory_usage": f"{memory_percent}%",
            "analyses_in_memory": len(analysis_store),
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

---

## 📧 Get Help

### 🔄 Still Having Issues?

1. **Check Platform Status:**
   - [Render Status](https://status.render.com/)
   - [Vercel Status](https://www.vercel-status.com/)
   - [GitHub Status](https://www.githubstatus.com/)

2. **Create Support Issue:**
   ```markdown
   **Environment:**
   - Platform: Render/Vercel/Fly.io
   - Browser: Chrome/Firefox/Safari
   - Error: [Exact error message]
   
   **Steps to Reproduce:**
   1. Go to...
   2. Click on...
   3. See error...
   
   **Expected vs Actual:**
   - Expected: Should work normally
   - Actual: Error occurred
   ```

3. **Community Support:**
   - 🐛 [GitHub Issues](https://github.com/Gzeu/viralsafe-platform-free/issues)
   - 💬 [GitHub Discussions](https://github.com/Gzeu/viralsafe-platform-free/discussions)
   - 📧 Email: Create an issue instead

### 🛠️ Emergency Recovery

**If everything is broken:**

1. **Redeploy from scratch:**
   ```bash
   # Fork repo again
   # Deploy to new Render service
   # Update frontend URL
   # Test functionality
   ```

2. **Rollback to working version:**
   ```bash
   # Find last working commit
   git log --oneline
   
   # Reset to working commit
   git reset --hard COMMIT_HASH
   git push --force-with-lease
   ```

---

**✨ Remember: Most issues are environment variable or configuration problems. Double-check your settings first!**