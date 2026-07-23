// ===== شريط التنقل السفلي: تفعيل العنصر النشط عند التمرير =====
document.addEventListener('DOMContentLoaded', () => {
    const sections = document.querySelectorAll('section[id]');
    const navItems = document.querySelectorAll('.nav-item');

    // تحديث العنصر النشط عند التمرير
    function updateActiveNav() {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 120;
            if (window.scrollY >= sectionTop) {
                current = section.getAttribute('id');
            }
        });

        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === `#${current}`) {
                item.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', updateActiveNav);

    // ===== تأثير الظهور بالتمرير (Intersection Observer) =====
    const animateElements = document.querySelectorAll('.card-animate, .fade-in');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // إذا كان العنصر من نوع fade-in (تم تفعيله تلقائياً)
                if (entry.target.classList.contains('fade-in')) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            }
        });
    }, {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    });

    animateElements.forEach(el => {
        // إذا كان العنصر غير مرئي، نضعه تحت المراقبة
        if (!el.classList.contains('visible')) {
            observer.observe(el);
        }
    });

    // ===== تحميل البيانات من نظام الإدارة (إن وجد) =====
    loadPortfolio();
    loadVideos();
    loadTestimonials();
    loadProfile();
});

// ===== دوال تحميل البيانات (نفس السابق) =====
async function fetchData(file) {
    try {
        const response = await fetch(file);
        if (!response.ok) throw new Error('فشل تحميل البيانات');
        return await response.json();
    } catch (error) {
        console.warn('خطأ في تحميل الملف:', file, error);
        return [];
    }
}

async function loadPortfolio() {
    const items = await fetchData('data/portfolio.json');
    const grid = document.getElementById('portfolio-grid');
    if (!grid) return;
    if (items.length === 0) {
        grid.innerHTML = `<p style="grid-column:1/-1; text-align:center; color:#777;">أضف مشاريعك من لوحة الإدارة</p>`;
        return;
    }
    grid.innerHTML = items.map(item => `
        <div class="portfolio-card card-animate">
            <img src="${item.image || 'https://via.placeholder.com/400x200/DBB5EE/4C0585?text=Project'}" alt="${item.title}">
            <h3>${item.title}</h3>
            <p>${item.description || ''}</p>
        </div>
    `).join('');
    // إعادة تفعيل المراقبة على البطاقات الجديدة
    document.querySelectorAll('.portfolio-card.card-animate').forEach(el => {
        observer.observe(el);
    });
}

async function loadVideos() {
    const items = await fetchData('data/videos.json');
    const grid = document.getElementById('videos-grid');
    if (!grid) return;
    if (items.length === 0) {
        grid.innerHTML = `<p style="grid-column:1/-1; text-align:center; color:#777;">أضف أعمال المونتاج من لوحة الإدارة</p>`;
        return;
    }
    grid.innerHTML = items.map(item => {
        let embedUrl = item.url;
        if (item.url.includes('youtube.com/watch?v=')) {
            const videoId = new URL(item.url).searchParams.get('v');
            embedUrl = `https://www.youtube.com/embed/${videoId}`;
        } else if (item.url.includes('youtu.be/')) {
            const videoId = item.url.split('/').pop();
            embedUrl = `https://www.youtube.com/embed/${videoId}`;
        } else if (item.url.includes('vimeo.com/')) {
            const videoId = item.url.split('/').pop();
            embedUrl = `https://player.vimeo.com/video/${videoId}`;
        }
        return `
            <div class="video-card card-animate">
                <div class="video-wrapper">
                    <iframe src="${embedUrl}" allowfullscreen loading="lazy"></iframe>
                </div>
                <h3>${item.title}</h3>
                <p>${item.description || ''}</p>
            </div>
        `;
    }).join('');
    document.querySelectorAll('.video-card.card-animate').forEach(el => {
        observer.observe(el);
    });
}

async function loadTestimonials() {
    const items = await fetchData('data/testimonials.json');
    const grid = document.getElementById('testimonials-grid');
    if (!grid) return;
    if (items.length === 0) {
        grid.innerHTML = `<p style="grid-column:1/-1; text-align:center; color:#777;">أضف آراء العملاء من لوحة الإدارة</p>`;
        return;
    }
    grid.innerHTML = items.map(item => `
        <div class="testimonial-card card-animate">
            <p class="quote">“${item.text}”</p>
            <p class="client-name">- ${item.name}</p>
            <p class="client-role">${item.role || ''}</p>
        </div>
    `).join('');
    document.querySelectorAll('.testimonial-card.card-animate').forEach(el => {
        observer.observe(el);
    });
}

async function loadProfile() {
    try {
        const response = await fetch('data/settings.json');
        if (!response.ok) return;
        const settings = await response.json();
        const img = document.getElementById('profile-image');
        if (img && settings.profile_image) {
            img.src = settings.profile_image;
        }
        const bio = document.getElementById('bio-text');
        if (bio && settings.bio_text) {
            bio.textContent = settings.bio_text;
        }
    } catch (e) {
        console.log('لا توجد إعدادات مخصصة.');
    }
}

// ===== متغير للـ observer لإعادة استخدامه =====
let observer;

// نعيد تعريف الـ observer خارجياً لاستخدامه في دوال التحميل
document.addEventListener('DOMContentLoaded', () => {
    observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });
});