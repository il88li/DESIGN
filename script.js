// ===== تفعيل شريط التنقل الدائري =====
document.addEventListener('DOMContentLoaded', () => {
    // تحديث العنصر النشط عند التمرير (للمساعدة في الصفحات الطويلة)
    const sections = document.querySelectorAll('section[id]');
    const navItems = document.querySelectorAll('.navbar-glass .nav-item');

    function updateActiveNav() {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 150;
            if (window.scrollY >= sectionTop) {
                current = section.getAttribute('id');
            }
        });
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') && item.getAttribute('href').includes(current)) {
                item.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', updateActiveNav);

    // ===== تأثير الظهور بالتمرير =====
    const animateElements = document.querySelectorAll('.card-animate, .fade-in');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                if (entry.target.classList.contains('fade-in')) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });

    animateElements.forEach(el => {
        if (!el.classList.contains('visible')) {
            observer.observe(el);
        }
    });
});