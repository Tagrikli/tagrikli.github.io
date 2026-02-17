/**
 * Starry background with twinkling stars
 * 
 * Configuration options (can be set via window.starryConfig before page load):
 * - starCount: number | null - Fixed number of stars, or null for auto-density (default: null)
 * - starDensity: number - Stars per 5000 pixels when starCount is null (default: 0.5)
 */

// Default configuration
const DEFAULT_CONFIG = {
    starCount: null,
    starDensity: 0.5
};

// Star colors
const STAR_COLORS = [
    '#ffffff',  // White
    '#fffafa',  // Snow
    '#f0f8ff',  // Alice Blue
    '#f5f5f5',  // White Smoke
    '#e8e8e8',  // Light gray
    '#add8e6',  // Light blue (for variety)
    '#fffacd',  // Lemon chiffon (slight yellow)
];

class StarryBackground {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.stars = [];
        this.animationId = null;

        // Merge user config with defaults
        this.config = { ...DEFAULT_CONFIG, ...window.starryConfig };

        this.init();
    }

    init() {
        // Create canvas element
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'star-canvas';
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.zIndex = '-2';
        this.canvas.style.pointerEvents = 'none';

        document.body.insertBefore(this.canvas, document.body.firstChild);

        this.ctx = this.canvas.getContext('2d');
        this.resize();

        // Create initial stars
        this.createStars();

        // Start animation
        this.animate();

        // Event listeners
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;

        // Recreate stars on resize
        if (this.stars.length > 0) {
            this.createStars();
        }
    }

    createStars() {
        this.stars = [];

        // Use fixed star count if provided, otherwise calculate based on density
        let numStars;
        if (this.config.starCount !== null) {
            numStars = this.config.starCount;
        } else {
            numStars = Math.floor((this.canvas.width * this.canvas.height) / 5000 * this.config.starDensity);
        }

        for (let i = 0; i < numStars; i++) {
            this.stars.push(this.createStar());
        }
    }

    createStar() {
        return {
            x: Math.random() * this.canvas.width,
            y: Math.random() * this.canvas.height,
            radius: Math.random() * 1.5 + 0.5, // 0.5 to 2 pixels
            color: STAR_COLORS[Math.floor(Math.random() * STAR_COLORS.length)],
            twinkleSpeed: Math.random() * 0.02 + 0.005,
            twinklePhase: Math.random() * Math.PI * 2,
            baseOpacity: Math.random() * 0.5 + 0.5
        };
    }

    drawStar(star) {
        const twinkle = Math.sin(star.twinklePhase) * 0.3 + 0.7;
        const currentOpacity = star.baseOpacity * twinkle;

        this.ctx.beginPath();
        this.ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
        this.ctx.fillStyle = star.color;
        this.ctx.globalAlpha = currentOpacity;
        this.ctx.fill();
        this.ctx.globalAlpha = 1;

        // Add subtle glow for brighter stars
        if (star.radius > 1) {
            const glowRadius = star.radius * 2;
            this.ctx.beginPath();
            this.ctx.arc(star.x, star.y, glowRadius, 0, Math.PI * 2);
            const gradient = this.ctx.createRadialGradient(
                star.x, star.y, 0,
                star.x, star.y, glowRadius
            );
            gradient.addColorStop(0, star.color);
            gradient.addColorStop(1, 'transparent');
            this.ctx.fillStyle = gradient;
            this.ctx.globalAlpha = currentOpacity * 0.3;
            this.ctx.fill();
            this.ctx.globalAlpha = 1;
        }
    }

    updateStars() {
        for (const star of this.stars) {
            star.twinklePhase += star.twinkleSpeed;
        }
    }

    animate() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Update and draw stars
        this.updateStars();
        for (const star of this.stars) {
            this.drawStar(star);
        }

        this.animationId = requestAnimationFrame(() => this.animate());
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
    }
}

// Initialize when DOM is ready
export function initStars() {
    // Only initialize if not already present
    if (!document.getElementById('star-canvas')) {
        new StarryBackground();
    }
}

// Auto-initialize
if (typeof window !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => initStars());
    } else {
        initStars();
    }
}
