import base64
from typing import Dict, Optional
from datetime import datetime
import hashlib

class BadgeGenerator:
    """Generate SVG badges for website verification status"""
    
    def __init__(self):
        self.base_url = "https://viralsafe-backend.onrender.com"
    
    def generate_verified_badge(self, domain: str, safety_score: float, style: str = "modern") -> str:
        """Generate a verified badge SVG"""
        
        if style == "modern":
            return self._create_modern_verified_badge(domain, safety_score)
        elif style == "shield":
            return self._create_shield_badge(domain, safety_score)
        elif style == "minimal":
            return self._create_minimal_badge(domain, safety_score)
        else:
            return self._create_classic_badge(domain, safety_score)
    
    def generate_warning_badge(self, domain: str, safety_score: float, style: str = "modern") -> str:
        """Generate a warning badge SVG for potentially unsafe sites"""
        
        if style == "modern":
            return self._create_modern_warning_badge(domain, safety_score)
        else:
            return self._create_classic_warning_badge(domain, safety_score)
    
    def _create_modern_verified_badge(self, domain: str, safety_score: float) -> str:
        """Create modern style verified badge"""
        score_percent = int(safety_score * 100)
        
        svg = f'''<svg width="200" height="40" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ViralSafe: Verified">
    <defs>
        <linearGradient id="verified-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#059669;stop-opacity:1" />
        </linearGradient>
        <filter id="drop-shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000000" flood-opacity="0.1"/>
        </filter>
    </defs>
    
    <!-- Background -->
    <rect width="200" height="40" rx="20" fill="url(#verified-gradient)" filter="url(#drop-shadow)"/>
    
    <!-- Shield Icon -->
    <g transform="translate(12, 8)">
        <path d="M12 1L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 1ZM10.5 16L6 11.5L7.41 10.09L10.5 13.17L16.59 7.09L18 8.5L10.5 16Z" 
              fill="white" transform="scale(0.8)"/>
    </g>
    
    <!-- Text -->
    <text x="40" y="15" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" 
          font-size="11" font-weight="600" fill="white">ViralSafe</text>
    <text x="40" y="28" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif" 
          font-size="9" fill="rgba(255,255,255,0.9)">Verified ({score_percent}%)</text>
    
    <!-- Click area -->
    <a href="{self.base_url}/verify/{domain}" target="_blank">
        <rect width="200" height="40" rx="20" fill="transparent"/>
    </a>
</svg>'''
        return svg
    
    def _create_shield_badge(self, domain: str, safety_score: float) -> str:
        """Create shield style badge"""
        score_percent = int(safety_score * 100)
        
        svg = f'''<svg width="120" height="120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ViralSafe Shield">
    <defs>
        <linearGradient id="shield-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#059669;stop-opacity:1" />
        </linearGradient>
    </defs>
    
    <!-- Shield Shape -->
    <path d="M60 10L20 25V55C20 80 35 100 60 110C85 100 100 80 100 55V25L60 10Z" 
          fill="url(#shield-gradient)" stroke="#047857" stroke-width="2"/>
    
    <!-- Checkmark -->
    <path d="M45 65L38 58L41 55L45 59L59 45L62 48L45 65Z" fill="white" stroke="white" stroke-width="2"/>
    
    <!-- Text -->
    <text x="60" y="85" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,sans-serif" 
          font-size="10" font-weight="600" fill="white">VERIFIED</text>
    <text x="60" y="96" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,sans-serif" 
          font-size="8" fill="rgba(255,255,255,0.9)">{score_percent}% Safe</text>
    
    <!-- Click area -->
    <a href="{self.base_url}/verify/{domain}" target="_blank">
        <rect width="120" height="120" fill="transparent"/>
    </a>
</svg>'''
        return svg
    
    def _create_minimal_badge(self, domain: str, safety_score: float) -> str:
        """Create minimal style badge"""
        score_percent = int(safety_score * 100)
        
        svg = f'''<svg width="100" height="20" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ViralSafe">
    <!-- Background -->
    <rect width="100" height="20" rx="3" fill="#10b981"/>
    
    <!-- Icon -->
    <circle cx="12" cy="10" r="6" fill="white"/>
    <path d="M9 10L11 12L15 8" stroke="#10b981" stroke-width="1.5" fill="none"/>
    
    <!-- Text -->
    <text x="22" y="14" font-family="-apple-system,BlinkMacSystemFont,sans-serif" 
          font-size="11" font-weight="500" fill="white">Safe {score_percent}%</text>
    
    <!-- Click area -->
    <a href="{self.base_url}/verify/{domain}" target="_blank">
        <rect width="100" height="20" fill="transparent"/>
    </a>
</svg>'''
        return svg
    
    def _create_classic_badge(self, domain: str, safety_score: float) -> str:
        """Create classic style badge"""
        score_percent = int(safety_score * 100)
        
        svg = f'''<svg width="140" height="30" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ViralSafe Verified">
    <defs>
        <linearGradient id="classic-bg" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#f8f9fa;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#e9ecef;stop-opacity:1" />
        </linearGradient>
    </defs>
    
    <!-- Background -->
    <rect width="140" height="30" rx="5" fill="url(#classic-bg)" stroke="#10b981" stroke-width="2"/>
    
    <!-- Icon -->
    <circle cx="20" cy="15" r="8" fill="#10b981"/>
    <path d="M16 15L18 17L24 11" stroke="white" stroke-width="2" fill="none"/>
    
    <!-- Text -->
    <text x="35" y="12" font-family="Arial,sans-serif" font-size="10" font-weight="bold" fill="#374151">ViralSafe</text>
    <text x="35" y="22" font-family="Arial,sans-serif" font-size="8" fill="#6b7280">Verified {score_percent}%</text>
    
    <!-- Click area -->
    <a href="{self.base_url}/verify/{domain}" target="_blank">
        <rect width="140" height="30" fill="transparent"/>
    </a>
</svg>'''
        return svg
    
    def _create_modern_warning_badge(self, domain: str, safety_score: float) -> str:
        """Create modern warning badge"""
        score_percent = int(safety_score * 100)
        
        svg = f'''<svg width="200" height="40" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ViralSafe: Warning">
    <defs>
        <linearGradient id="warning-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#f59e0b;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#d97706;stop-opacity:1" />
        </linearGradient>
    </defs>
    
    <!-- Background -->
    <rect width="200" height="40" rx="20" fill="url(#warning-gradient)"/>
    
    <!-- Warning Icon -->
    <g transform="translate(12, 8)">
        <path d="M12 2L1 21H23L12 2ZM12 18H12V18ZM12 14H12V10H12" 
              fill="white" transform="scale(0.8)"/>
        <circle cx="9.6" cy="14.4" r="1" fill="#f59e0b"/>
    </g>
    
    <!-- Text -->
    <text x="40" y="15" font-family="-apple-system,BlinkMacSystemFont,sans-serif" 
          font-size="11" font-weight="600" fill="white">ViralSafe</text>
    <text x="40" y="28" font-family="-apple-system,BlinkMacSystemFont,sans-serif" 
          font-size="9" fill="rgba(255,255,255,0.9)">Warning ({score_percent}%)</text>
    
    <!-- Click area -->
    <a href="{self.base_url}/verify/{domain}" target="_blank">
        <rect width="200" height="40" fill="transparent"/>
    </a>
</svg>'''
        return svg
    
    def _create_classic_warning_badge(self, domain: str, safety_score: float) -> str:
        """Create classic warning badge"""
        score_percent = int(safety_score * 100)
        
        svg = f'''<svg width="140" height="30" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ViralSafe Warning">
    <!-- Background -->
    <rect width="140" height="30" rx="5" fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>
    
    <!-- Warning Icon -->
    <g transform="translate(12, 8)">
        <path d="M7 1L1 11H13L7 1ZM7 9H7V9ZM7 7H7V4H7" 
              fill="#f59e0b" transform="scale(1)"/>
        <circle cx="7" cy="8" r="0.5" fill="#fef3c7"/>
    </g>
    
    <!-- Text -->
    <text x="35" y="12" font-family="Arial,sans-serif" font-size="10" font-weight="bold" fill="#92400e">ViralSafe</text>
    <text x="35" y="22" font-family="Arial,sans-serif" font-size="8" fill="#b45309">Warning {score_percent}%</text>
    
    <!-- Click area -->
    <a href="{self.base_url}/verify/{domain}" target="_blank">
        <rect width="140" height="30" fill="transparent"/>
    </a>
</svg>'''
        return svg
    
    def generate_embed_code(self, domain: str, style: str = "modern", format: str = "html") -> str:
        """Generate embed code for badges"""
        
        badge_url = f"{self.base_url}/badge/verified/{domain}?style={style}"
        verify_url = f"{self.base_url}/verify/{domain}"
        
        if format == "html":
            return f'''<!-- ViralSafe Badge pentru {domain} -->
<a href="{verify_url}" target="_blank" rel="noopener">
    <img src="{badge_url}" alt="Verificat de ViralSafe" title="Site verificat pentru siguranță de ViralSafe"/>
</a>'''
        
        elif format == "markdown":
            return f"[![ViralSafe Verified]({badge_url})]({verify_url})"
        
        elif format == "bbcode":
            return f"[url={verify_url}][img]{badge_url}[/img][/url]"
        
        else:
            return badge_url
    
    def generate_widget_code(self, domain: str, options: Dict = None) -> str:
        """Generate JavaScript widget code"""
        
        default_options = {
            "position": "bottom-right",
            "theme": "light",
            "showScore": True,
            "autoHide": False
        }
        
        if options:
            default_options.update(options)
        
        widget_code = f'''<!-- ViralSafe Widget pentru {domain} -->
<script>
(function() {{
    const ViralSafeWidget = {{
        domain: '{domain}',
        options: {default_options},
        
        init: function() {{
            this.createWidget();
            this.checkDomain();
        }},
        
        createWidget: function() {{
            const widget = document.createElement('div');
            widget.id = 'viralsafe-widget';
            widget.innerHTML = `
                <div class="vs-widget vs-${{this.options.theme}} vs-${{this.options.position}}">
                    <div class="vs-badge" onclick="ViralSafeWidget.showDetails()">
                        <span class="vs-icon">🛡️</span>
                        <span class="vs-text">ViralSafe</span>
                        <span class="vs-status">Checking...</span>
                    </div>
                </div>
            `;
            
            // Add styles
            const style = document.createElement('style');
            style.textContent = `
                #viralsafe-widget {{
                    position: fixed;
                    z-index: 9999;
                    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                }}
                .vs-widget.vs-bottom-right {{ bottom: 20px; right: 20px; }}
                .vs-widget.vs-bottom-left {{ bottom: 20px; left: 20px; }}
                .vs-badge {{
                    background: linear-gradient(135deg, #10b981, #059669);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 25px;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    transition: transform 0.2s;
                }}
                .vs-badge:hover {{ transform: translateY(-2px); }}
            `;
            
            document.head.appendChild(style);
            document.body.appendChild(widget);
        }},
        
        async checkDomain() {{
            try {{
                const response = await fetch(`{self.base_url}/verify/${{this.domain}}`);
                const result = await response.json();
                this.updateWidget(result);
            }} catch (error) {{
                console.log('ViralSafe verification failed:', error);
            }}
        }},
        
        updateWidget: function(result) {{
            const statusEl = document.querySelector('.vs-status');
            if (statusEl) {{
                if (result.verified) {{
                    statusEl.textContent = 'Verified';
                    statusEl.style.color = '#dcfce7';
                }} else {{
                    statusEl.textContent = 'Warning';
                    statusEl.style.color = '#fef3c7';
                }}
            }}
        }},
        
        showDetails: function() {{
            window.open(`{self.base_url}/verify/${{this.domain}}`, '_blank');
        }}
    }};
    
    // Auto-init when DOM is ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', () => ViralSafeWidget.init());
    }} else {{
        ViralSafeWidget.init();
    }}
    
    window.ViralSafe = ViralSafeWidget;
}})();
</script>'''
        
        return widget_code

# Singleton instance
badge_generator = BadgeGenerator()