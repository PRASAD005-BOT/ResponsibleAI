/**
 * AI Ethics Platform - Enhanced UI Effects
 * Provides modern animations and interactive effects
 */

document.addEventListener('DOMContentLoaded', function() {
    try {
        // Initialize enhanced UI effects
        initAnimations();
        initScrollEffects();
        initParallaxEffects();
        initTypingEffect();
        initCountUpAnimation();
        initRippleEffect();
        initImageEffects();
        
        console.log('Enhanced UI effects initialized');
    } catch (error) {
        console.log('Enhanced UI initialization error:', error.message);
    }
});

/**
 * Initialize animations for elements
 */
function initAnimations() {
    // Add fade-in class to cards
    document.querySelectorAll('.card, .stat-card').forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('fade-in');
        }, index * 100); // Stagger the animations
    });
    
    // Initialize staggered animations for list items
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const appearOnScroll = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            
            if (entry.target.classList.contains('staggered-container')) {
                const items = entry.target.querySelectorAll('.staggered-item');
                items.forEach((item, index) => {
                    setTimeout(() => {
                        item.classList.add('visible');
                    }, index * 100);
                });
            } else {
                entry.target.classList.add('visible');
            }
            
            observer.unobserve(entry.target);
        });
    }, observerOptions);
    
    // Observe elements with animation classes
    document.querySelectorAll('.staggered-container, .chart-container, .fade-in-section').forEach(item => {
        appearOnScroll.observe(item);
        
        // Add staggered-item class to children of staggered containers
        if (item.classList.contains('staggered-container')) {
            item.querySelectorAll('li, .card, .feature-list li').forEach(child => {
                child.classList.add('staggered-item');
            });
        }
    });
}

/**
 * Initialize scroll-based effects
 */
function initScrollEffects() {
    try {
        // Navbar scroll effect
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 50) {
                    navbar.classList.add('navbar-scrolled');
                } else {
                    navbar.classList.remove('navbar-scrolled');
                }
            });
        }
        
        // Parallax scroll for dashboard header
        const dashboardHeader = document.querySelector('.dashboard-header');
        if (dashboardHeader) {
            window.addEventListener('scroll', () => {
                const scrollValue = window.scrollY;
                dashboardHeader.style.backgroundPositionY = scrollValue * 0.4 + 'px';
            });
        }
    } catch (error) {
        console.log('Error in initScrollEffects:', error.message);
    }
    
    // Progress bar animations on scroll
    const progressBars = document.querySelectorAll('.progress-bar');
    if (progressBars.length > 0) {
        const progressObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const width = entry.target.getAttribute('data-width') || '0';
                    const value = entry.target.getAttribute('data-value') || '0%';
                    entry.target.style.width = width;
                    entry.target.setAttribute('data-value', value);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        progressBars.forEach(bar => {
            // Store the target width
            const width = bar.style.width;
            bar.style.width = '0%';
            bar.setAttribute('data-width', width);
            
            // Observe the progress bar
            progressObserver.observe(bar);
        });
    }
}

/**
 * Initialize parallax effects
 */
function initParallaxEffects() {
    const parallaxElements = document.querySelectorAll('.parallax');
    
    if (parallaxElements.length > 0) {
        window.addEventListener('mousemove', (e) => {
            const x = e.clientX / window.innerWidth;
            const y = e.clientY / window.innerHeight;
            
            parallaxElements.forEach(element => {
                const speed = element.getAttribute('data-speed') || 5;
                const xOffset = (0.5 - x) * speed;
                const yOffset = (0.5 - y) * speed;
                
                element.style.transform = `translate(${xOffset}px, ${yOffset}px)`;
            });
        });
    }
}

/**
 * Initialize typing effect for headings
 */
function initTypingEffect() {
    const typingElements = document.querySelectorAll('.typing-effect');
    
    typingElements.forEach(element => {
        const text = element.textContent;
        const speed = parseInt(element.getAttribute('data-speed')) || 50;
        
        element.textContent = '';
        element.style.borderRight = '0.1em solid var(--primary-color)';
        
        let i = 0;
        function typeWriter() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, speed);
            } else {
                element.style.borderRight = 'none';
            }
        }
        
        setTimeout(typeWriter, 500);
    });
}

/**
 * Initialize count-up animation for statistical values
 */
function initCountUpAnimation() {
    const countElements = document.querySelectorAll('.stat-value');
    
    if (countElements.length > 0) {
        const countObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const target = parseFloat(element.getAttribute('data-target')) || 0;
                    const duration = parseInt(element.getAttribute('data-duration')) || 2000;
                    const decimals = parseInt(element.getAttribute('data-decimals')) || 0;
                    
                    element.classList.add('animate');
                    
                    let startTime = null;
                    const startValue = 0;
                    
                    function animateCount(timestamp) {
                        if (!startTime) startTime = timestamp;
                        
                        const progress = Math.min((timestamp - startTime) / duration, 1);
                        const currentValue = startValue + (progress * (target - startValue));
                        
                        element.textContent = currentValue.toFixed(decimals);
                        
                        if (progress < 1) {
                            window.requestAnimationFrame(animateCount);
                        } else {
                            element.textContent = target.toFixed(decimals);
                        }
                    }
                    
                    window.requestAnimationFrame(animateCount);
                    observer.unobserve(element);
                }
            });
        }, { threshold: 0.1 });
        
        countElements.forEach(element => {
            // Store the target value
            const value = parseFloat(element.textContent.replace(/[^0-9.-]+/g, ''));
            element.setAttribute('data-target', value);
            element.textContent = '0';
            
            // Observe the element
            countObserver.observe(element);
        });
    }
}

/**
 * Initialize ripple effect for buttons and cards
 */
function initRippleEffect() {
    // Add ripple class to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.classList.add('ripple');
    });
    
    // Add click event listener to ripple elements
    document.addEventListener('click', function(e) {
        const target = e.target;
        if (target.classList.contains('ripple')) {
            const rect = target.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            target.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        }
    });
}

/**
 * Initialize image effects
 */
function initImageEffects() {
    // Add tilt effect to images
    document.querySelectorAll('.tilt-effect').forEach(element => {
        element.addEventListener('mousemove', (e) => {
            const boundingRect = element.getBoundingClientRect();
            const x = e.clientX - boundingRect.left;
            const y = e.clientY - boundingRect.top;
            
            const xPercent = x / boundingRect.width;
            const yPercent = y / boundingRect.height;
            
            const rotateX = (0.5 - yPercent) * 10;
            const rotateY = (xPercent - 0.5) * 10;
            
            element.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });
        
        element.addEventListener('mouseleave', () => {
            element.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
        });
    });
    
    // Add hover zoom effect
    document.querySelectorAll('.zoom-effect').forEach(element => {
        element.addEventListener('mouseenter', () => {
            element.style.transform = 'scale(1.05)';
            element.style.zIndex = '1';
        });
        
        element.addEventListener('mouseleave', () => {
            element.style.transform = 'scale(1)';
            element.style.zIndex = '';
        });
    });
}

/**
 * Add particle background effect to element
 * @param {string} elementId - ID of element to add particles to
 * @param {Object} options - Particle options
 */
function addParticleBackground(elementId, options = {}) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Default options
    const defaultOptions = {
        particleCount: 50,
        color: 'rgba(255, 255, 255, 0.5)',
        minSize: 1,
        maxSize: 3,
        speed: 1
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    // Create canvas
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '0';
    
    element.style.position = 'relative';
    element.insertBefore(canvas, element.firstChild);
    
    function resizeCanvas() {
        canvas.width = element.offsetWidth;
        canvas.height = element.offsetHeight;
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Create particles
    const particles = [];
    
    for (let i = 0; i < finalOptions.particleCount; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * (finalOptions.maxSize - finalOptions.minSize) + finalOptions.minSize,
            speedX: (Math.random() - 0.5) * finalOptions.speed,
            speedY: (Math.random() - 0.5) * finalOptions.speed
        });
    }
    
    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            // Update position
            particle.x += particle.speedX;
            particle.y += particle.speedY;
            
            // Wrap around edges
            if (particle.x < 0) particle.x = canvas.width;
            if (particle.x > canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = canvas.height;
            if (particle.y > canvas.height) particle.y = 0;
            
            // Draw particle
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fillStyle = finalOptions.color;
            ctx.fill();
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
}

/**
 * Creates a 3D card effect
 * @param {string} selector - CSS selector for cards
 */
function create3DCardEffect(selector) {
    const cards = document.querySelectorAll(selector);
    
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const angleY = (x - centerX) / 8;
            const angleX = (centerY - y) / 8;
            
            card.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg)';
        });
    });
}

/**
 * Creates a wavy background effect
 * @param {string} elementId - ID of element to add wave to
 * @param {Object} options - Wave options
 */
function createWaveEffect(elementId, options = {}) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Default options
    const defaultOptions = {
        color: 'rgba(255, 255, 255, 0.1)',
        amplitude: 20,
        period: 200,
        speed: 0.1,
        height: 100
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    // Create canvas
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.style.position = 'absolute';
    canvas.style.bottom = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = finalOptions.height + 'px';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '0';
    
    element.style.position = 'relative';
    element.appendChild(canvas);
    
    function resizeCanvas() {
        canvas.width = element.offsetWidth;
        canvas.height = finalOptions.height;
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    let phase = 0;
    
    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Update phase
        phase += finalOptions.speed;
        
        // Draw wave
        ctx.beginPath();
        ctx.moveTo(0, canvas.height);
        
        for (let x = 0; x < canvas.width; x++) {
            const y = Math.sin(x / finalOptions.period + phase) * finalOptions.amplitude + (canvas.height - finalOptions.amplitude);
            ctx.lineTo(x, y);
        }
        
        ctx.lineTo(canvas.width, canvas.height);
        ctx.closePath();
        ctx.fillStyle = finalOptions.color;
        ctx.fill();
        
        requestAnimationFrame(animate);
    }
    
    animate();
}