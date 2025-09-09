// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add scroll effect to navbar
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.05)';
    }
});

// Animate elements on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards
document.querySelectorAll('.feature-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
});

// Observe steps
document.querySelectorAll('.step').forEach((step, index) => {
    step.style.opacity = '0';
    step.style.transform = 'translateY(20px)';
    step.style.transition = `opacity 0.6s ease ${index * 0.2}s, transform 0.6s ease ${index * 0.2}s`;
    observer.observe(step);
});

// Observe impact cards
document.querySelectorAll('.impact-card').forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = `opacity 0.6s ease ${index * 0.15}s, transform 0.6s ease ${index * 0.15}s`;
    observer.observe(card);
});

// Add hover effect to buttons
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
    });
    button.addEventListener('mouseleave', function() {
        if (!this.classList.contains('btn-primary')) {
            this.style.transform = 'translateY(0)';
        }
    });
});

// Counter animation for stats
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = element.getAttribute('data-format').replace('{value}', target);
            clearInterval(timer);
        } else {
            element.textContent = element.getAttribute('data-format').replace('{value}', Math.floor(start));
        }
    }, 16);
}

// Animate stats when they come into view
const statsObserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
            entry.target.classList.add('animated');
            const statNumber = entry.target.querySelector('.stat-number');
            const text = statNumber.textContent;
            
            if (text.includes('1.75M')) {
                statNumber.setAttribute('data-format', '{value}M');
                animateCounter(statNumber, 1.75);
            } else if (text.includes('50,000')) {
                statNumber.setAttribute('data-format', '₹{value}Cr');
                animateCounter(statNumber, 50000);
            } else if (text.includes('100')) {
                statNumber.setAttribute('data-format', '{value}%');
                animateCounter(statNumber, 100);
            }
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('.stat').forEach(stat => {
    statsObserver.observe(stat);
});

// Mobile menu toggle (for future mobile menu implementation)
function createMobileMenu() {
    const navbar = document.querySelector('.navbar .container');
    const menuButton = document.createElement('button');
    menuButton.className = 'mobile-menu-toggle';
    menuButton.innerHTML = '<i class="fas fa-bars"></i>';
    menuButton.style.display = 'none';
    
    // Show mobile menu button on small screens
    if (window.innerWidth <= 768) {
        menuButton.style.display = 'block';
        menuButton.style.position = 'absolute';
        menuButton.style.right = '20px';
        menuButton.style.background = 'none';
        menuButton.style.border = 'none';
        menuButton.style.fontSize = '1.5rem';
        menuButton.style.cursor = 'pointer';
        menuButton.style.color = 'var(--primary-color)';
    }
    
    navbar.appendChild(menuButton);
    
    menuButton.addEventListener('click', function() {
        const navLinks = document.querySelector('.nav-links');
        navLinks.classList.toggle('mobile-active');
    });
}

// Initialize mobile menu on load
document.addEventListener('DOMContentLoaded', createMobileMenu);

// Handle window resize
window.addEventListener('resize', function() {
    const menuButton = document.querySelector('.mobile-menu-toggle');
    if (menuButton) {
        menuButton.style.display = window.innerWidth <= 768 ? 'block' : 'none';
    }
});

// Add loading animation to GitHub buttons
document.querySelectorAll('a[href*="github.com"]').forEach(link => {
    link.addEventListener('click', function(e) {
        const icon = this.querySelector('i.fab.fa-github');
        if (icon) {
            icon.classList.add('fa-spin');
            setTimeout(() => {
                icon.classList.remove('fa-spin');
            }, 1000);
        }
    });
});

// Add typing effect to hero title (optional enhancement)
function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.textContent = '';
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// Optional: Add typing effect to hero title on load
// Uncomment if you want this effect
// document.addEventListener('DOMContentLoaded', function() {
//     const heroTitle = document.querySelector('.hero-title');
//     if (heroTitle) {
//         const originalText = heroTitle.textContent;
//         typeWriter(heroTitle, originalText, 30);
//     }
// });

console.log('BitWipers website loaded successfully!');
console.log('Visit https://github.com/your-org/BitWipers to get started.');
