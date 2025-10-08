#!/bin/bash

# 🚀 ViralSafe Platform - Automated Deployment Script
# Deploy to Render.com, Fly.io, or Vercel with one command

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis for better UX
ROCKET="🚀"
CHECK="✅"
WARNING="⚠️"
ERROR="❌"
INFO="📝"
COG="⚙️"
GLOBE="🌍"

# Script info
echo -e "${PURPLE}${ROCKET} ViralSafe Platform - Auto Deployment${NC}"
echo -e "${CYAN}Version: 1.0.0 | Platform: Multi-Cloud${NC}"
echo -e "${BLUE}Repository: https://github.com/Gzeu/viralsafe-platform-free${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${ERROR} ${RED}Error: Please run this script from the project root directory${NC}"
    echo -e "${INFO} Expected structure: README.md, backend/, frontend/"
    exit 1
fi

echo -e "${CHECK} ${GREEN}Project structure verified${NC}"

# Platform selection menu
echo -e "${ROCKET} ${YELLOW}Choose your deployment platform:${NC}"
echo ""
echo -e "${CYAN}1)${NC} 🌐 Render.com (FREE - Recommended)"
echo -e "   ${GREEN}•${NC} 512MB RAM, 750h/month"
echo -e "   ${GREEN}•${NC} Auto-sleep after 15min"
echo -e "   ${GREEN}•${NC} $0/month forever"
echo ""
echo -e "${CYAN}2)${NC} ✈️ Fly.io (Performance)"
echo -e "   ${GREEN}•${NC} 1GB RAM, $5 credit monthly"
echo -e "   ${GREEN}•${NC} No sleep policy"
echo -e "   ${GREEN}•${NC} Better performance"
echo ""
echo -e "${CYAN}3)${NC} ⚡ Vercel (Full-Stack)"
echo -e "   ${GREEN}•${NC} Frontend + Serverless backend"
echo -e "   ${GREEN}•${NC} Global edge deployment"
echo -e "   ${GREEN}•${NC} Instant scaling"
echo ""
echo -e "${CYAN}4)${NC} 📊 Status Check (Existing deployment)"
echo -e "   ${GREEN}•${NC} Check current platform health"
echo -e "   ${GREEN}•${NC} Test API endpoints"
echo -e "   ${GREEN}•${NC} Performance metrics"
echo ""
echo -e "${CYAN}5)${NC} 🚑 Emergency Recovery"
echo -e "   ${GREEN}•${NC} Quick redeploy if something broke"
echo -e "   ${GREEN}•${NC} Reset and start fresh"
echo ""

read -p "$(echo -e ${YELLOW}Select option [1-5]: ${NC})" choice

case $choice in
    1)
        echo -e "${ROCKET} ${GREEN}Deploying to Render.com${NC}"
        echo ""
        echo -e "${INFO} ${BLUE}Setting up Render.com deployment...${NC}"
        
        # Check if render.yaml exists
        if [ ! -f "render.yaml" ]; then
            echo -e "${WARNING} render.yaml not found, creating...${NC}"
            cat > render.yaml << 'EOF'
services:
  - type: web
    name: viralsafe-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port 10000
    plan: free
    rootDir: backend
    healthCheckPath: /health
    envVars:
      - key: PORT
        value: 10000
      - key: ENVIRONMENT
        value: production
      - key: CORS_ORIGINS
        value: "*"
EOF
            echo -e "${CHECK} render.yaml created${NC}"
        fi
        
        echo -e "${GLOBE} ${CYAN}Opening Render.com deployment page...${NC}"
        echo ""
        echo -e "${INFO} Steps to complete deployment:"
        echo -e "  1. Click the deploy button that will open"
        echo -e "  2. Connect your GitHub account"
        echo -e "  3. Select this repository: $(basename $(pwd))"
        echo -e "  4. Render will auto-detect the configuration"
        echo -e "  5. Click 'Deploy' and wait 2-3 minutes"
        echo -e "  6. Copy the URL when deployment completes"
        echo ""
        echo -e "${WARNING} ${YELLOW}Don't forget to update your frontend NEXT_PUBLIC_API_URL!${NC}"
        
        # Open deployment URL
        REPO_URL="https://github.com/Gzeu/viralsafe-platform-free"
        DEPLOY_URL="https://render.com/deploy?repo=${REPO_URL}"
        
        echo -e "${ROCKET} Opening: ${DEPLOY_URL}"
        
        # Try to open in browser (works on most systems)
        if command -v open >/dev/null 2>&1; then
            open "$DEPLOY_URL"
        elif command -v xdg-open >/dev/null 2>&1; then
            xdg-open "$DEPLOY_URL"
        elif command -v start >/dev/null 2>&1; then
            start "$DEPLOY_URL"
        else
            echo -e "${INFO} Please open this URL manually: ${DEPLOY_URL}"
        fi
        ;;
        
    2)
        echo -e "${ROCKET} ${GREEN}Deploying to Fly.io${NC}"
        echo ""
        
        # Check if flyctl is installed
        if ! command -v flyctl >/dev/null 2>&1; then
            echo -e "${WARNING} ${YELLOW}Fly CLI not found. Installing...${NC}"
            
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                if command -v brew >/dev/null 2>&1; then
                    brew install flyctl
                else
                    curl -L https://fly.io/install.sh | sh
                fi
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                # Linux
                curl -L https://fly.io/install.sh | sh
            else
                echo -e "${ERROR} Please install Fly CLI manually: https://fly.io/docs/getting-started/installing-flyctl/"
                exit 1
            fi
        fi
        
        echo -e "${CHECK} ${GREEN}Fly CLI found${NC}"
        
        # Login check
        if ! flyctl auth whoami >/dev/null 2>&1; then
            echo -e "${INFO} ${BLUE}Please login to Fly.io...${NC}"
            flyctl auth login
        fi
        
        echo -e "${CHECK} ${GREEN}Authenticated with Fly.io${NC}"
        
        # Deploy
        echo -e "${ROCKET} ${CYAN}Launching on Fly.io...${NC}"
        cd backend
        
        if [ ! -f "fly.toml" ]; then
            echo -e "${COG} ${BLUE}Initializing Fly app...${NC}"
            flyctl launch --generate-name --no-deploy
        fi
        
        echo -e "${ROCKET} ${CYAN}Deploying to Fly.io...${NC}"
        flyctl deploy
        
        echo -e "${CHECK} ${GREEN}Deployment completed!${NC}"
        
        # Get the URL
        APP_URL=$(flyctl info --json | jq -r '.Hostname' 2>/dev/null || echo "your-app.fly.dev")
        echo -e "${GLOBE} ${CYAN}Your API URL: https://${APP_URL}${NC}"
        
        cd ..
        ;;
        
    3)
        echo -e "${ROCKET} ${GREEN}Deploying to Vercel (Full-Stack)${NC}"
        echo ""
        
        # Frontend deployment
        echo -e "${INFO} ${BLUE}Setting up frontend deployment...${NC}"
        
        REPO_URL="https://github.com/Gzeu/viralsafe-platform-free"
        VERCEL_URL="https://vercel.com/new/clone?repository-url=${REPO_URL}"
        
        echo -e "${GLOBE} ${CYAN}Opening Vercel deployment...${NC}"
        echo ""
        echo -e "${INFO} Steps to complete:"
        echo -e "  1. Click the deploy button that will open"
        echo -e "  2. Connect your GitHub account"
        echo -e "  3. Clone the repository"
        echo -e "  4. Set root directory to: frontend"
        echo -e "  5. Add environment variable:"
        echo -e "     NEXT_PUBLIC_API_URL = (your backend URL)"
        echo -e "  6. Deploy!"
        
        if command -v open >/dev/null 2>&1; then
            open "$VERCEL_URL"
        elif command -v xdg-open >/dev/null 2>&1; then
            xdg-open "$VERCEL_URL"
        else
            echo -e "${INFO} Please open: ${VERCEL_URL}"
        fi
        ;;
        
    4)
        echo -e "${COG} ${GREEN}Checking deployment status...${NC}"
        echo ""
        
        # Get URLs from user
        read -p "$(echo -e ${CYAN}Enter your backend URL [https://your-app.onrender.com]: ${NC})" BACKEND_URL
        read -p "$(echo -e ${CYAN}Enter your frontend URL [https://your-app.vercel.app]: ${NC})" FRONTEND_URL
        
        if [ -n "$BACKEND_URL" ]; then
            echo -e "${INFO} ${BLUE}Testing backend health...${NC}"
            
            if curl -f -s "$BACKEND_URL/health" >/dev/null; then
                echo -e "${CHECK} ${GREEN}Backend is healthy${NC}"
                
                # Get health details
                HEALTH=$(curl -s "$BACKEND_URL/health")
                echo -e "${INFO} Response: $HEALTH"
                
                # Test API
                echo -e "${INFO} ${BLUE}Testing API endpoint...${NC}"
                API_TEST=$(curl -s -X POST "$BACKEND_URL/analyze" \
                    -H "Content-Type: application/json" \
                    -d '{"content":"test message","platform":"general"}')
                
                if [ $? -eq 0 ]; then
                    echo -e "${CHECK} ${GREEN}API is working${NC}"
                    echo -e "${INFO} Sample response: $(echo $API_TEST | head -c 100)..."
                else
                    echo -e "${ERROR} ${RED}API test failed${NC}"
                fi
            else
                echo -e "${ERROR} ${RED}Backend health check failed${NC}"
            fi
        fi
        
        if [ -n "$FRONTEND_URL" ]; then
            echo -e "${INFO} ${BLUE}Testing frontend...${NC}"
            
            if curl -f -s "$FRONTEND_URL" >/dev/null; then
                echo -e "${CHECK} ${GREEN}Frontend is accessible${NC}"
            else
                echo -e "${ERROR} ${RED}Frontend is not accessible${NC}"
            fi
        fi
        ;;
        
    5)
        echo -e "${WARNING} ${YELLOW}Emergency Recovery Mode${NC}"
        echo ""
        echo -e "${INFO} This will help you recover from deployment issues"
        echo ""
        echo -e "${CYAN}Recovery options:${NC}"
        echo -e "  1. Re-run deployment from scratch"
        echo -e "  2. Check common issues"
        echo -e "  3. Reset environment variables"
        echo -e "  4. View troubleshooting guide"
        echo ""
        
        read -p "$(echo -e ${YELLOW}What would you like to do? [1-4]: ${NC})" recovery_choice
        
        case $recovery_choice in
            1)
                echo -e "${ROCKET} ${CYAN}Restarting deployment process...${NC}"
                exec "$0"  # Restart this script
                ;;
            2)
                echo -e "${INFO} ${BLUE}Common deployment issues:${NC}"
                echo -e "  • Environment variables not set correctly"
                echo -e "  • Backend URL missing or wrong in frontend"
                echo -e "  • Platform service down or overloaded"
                echo -e "  • Build errors due to dependencies"
                echo -e "  • CORS issues between frontend and backend"
                ;;
            3)
                echo -e "${COG} ${BLUE}Environment variables checklist:${NC}"
                echo -e "  Backend (Render/Fly.io):"
                echo -e "    PORT=10000 (Render) or 8000 (Fly.io)"
                echo -e "    ENVIRONMENT=production"
                echo -e "    CORS_ORIGINS=*"
                echo -e "  Frontend (Vercel):"
                echo -e "    NEXT_PUBLIC_API_URL=https://your-backend-url"
                ;;
            4)
                echo -e "${INFO} ${BLUE}Opening troubleshooting guide...${NC}"
                GUIDE_URL="https://github.com/Gzeu/viralsafe-platform-free/blob/main/TROUBLESHOOTING.md"
                
                if command -v open >/dev/null 2>&1; then
                    open "$GUIDE_URL"
                elif command -v xdg-open >/dev/null 2>&1; then
                    xdg-open "$GUIDE_URL"
                else
                    echo -e "${INFO} Please visit: ${GUIDE_URL}"
                fi
                ;;
        esac
        ;;
        
    *)
        echo -e "${ERROR} ${RED}Invalid option. Please choose 1-5.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${CHECK} ${GREEN}Deployment script completed!${NC}"
echo -e "${INFO} ${BLUE}Next steps:${NC}"
echo -e "  1. Wait for deployment to complete (2-5 minutes)"
echo -e "  2. Test your endpoints"
echo -e "  3. Update frontend with backend URL if needed"
echo -e "  4. Set up monitoring and health checks"
echo ""
echo -e "${ROCKET} ${CYAN}Happy deploying!${NC}"
echo -e "${GLOBE} ${BLUE}Platform: https://github.com/Gzeu/viralsafe-platform-free${NC}"