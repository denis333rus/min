// Hero Slider Functionality
const slides = document.querySelectorAll('.hero-slide');
let currentSlide = 0;

function showSlide(index) {
    slides.forEach(slide => slide.classList.remove('active'));
    slides[index].classList.add('active');
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
}

// Auto-advance slides every 5 seconds
setInterval(nextSlide, 5000);

// News Animation on Scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInUp 0.6s ease-out';
            entry.target.style.opacity = '1';
        }
    });
}, observerOptions);

// Observe all cards for animation
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.news-card, .structure-card, .stat-item');
    cards.forEach(card => {
        card.style.opacity = '0';
        observer.observe(card);
    });
});

// Smooth Scrolling for Anchor Links
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

// Search Functionality
document.querySelector('.search-box button').addEventListener('click', function() {
    const searchInput = document.querySelector('.search-box input');
    const searchTerm = searchInput.value.trim();
    if (searchTerm) {
        alert(`Поиск: "${searchTerm}"\n\nФункция поиска будет реализована позже.`);
    }
});

// Enter key support for search
document.querySelector('.search-box input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        document.querySelector('.search-box button').click();
    }
});

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);

// Stats Counter Animation
function animateCounter(element, target, duration) {
    let start = 0;
    const increment = target / (duration / 16);
    
    function updateCounter() {
        start += increment;
        if (start < target) {
            element.textContent = Math.floor(start) + element.textContent.replace(/[0-9]/g, '').replace('.', '');
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target + element.textContent.replace(/[0-9]/g, '').replace('.', '');
        }
    }
    
    updateCounter();
}

// Animate stats when they come into view
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const statNumber = entry.target.querySelector('.stat-number');
            const fullText = statNumber.textContent;
            const number = parseFloat(fullText.replace(/[^\d.]/g, ''));
            const suffix = fullText.replace(/[\d.]/g, '');
            
            statNumber.textContent = '0' + suffix;
            animateCounter(statNumber, number, 2000);
            
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.stat-item').forEach(stat => {
        statsObserver.observe(stat);
    });
});

