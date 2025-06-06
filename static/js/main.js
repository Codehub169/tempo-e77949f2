document.addEventListener('DOMContentLoaded', () => {
    // Mobile navigation toggle
    const navToggle = document.querySelector('.nav-toggle');
    const mainNavUl = document.querySelector('.main-nav ul');

    if (navToggle && mainNavUl) {
        navToggle.addEventListener('click', () => {
            const isExpanded = mainNavUl.classList.toggle('active');
            navToggle.setAttribute('aria-expanded', isExpanded);
            // Change icon based on expanded state
            if (isExpanded) {
                navToggle.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" height="28px" viewBox="0 0 24 24" width="28px" fill="currentColor"><path d="M0 0h24v24H0V0z" fill="none"/><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/></svg>`;
            } else {
                navToggle.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" height="28px" viewBox="0 0 24 24" width="28px" fill="currentColor"><path d="M0 0h24v24H0V0z" fill="none"/><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>`;
            }
        });
    }

    // Set current year in footer
    const currentYearSpan = document.getElementById('currentYear');
    if (currentYearSpan) {
        currentYearSpan.textContent = new Date().getFullYear();
    }

    // Active navigation link highlighting
    const navLinks = document.querySelectorAll('.main-nav ul li a');
    const activePage = document.body.dataset.activePage; // Relies on <body data-active-page="{{ request.endpoint }}">

    navLinks.forEach(link => {
        link.classList.remove('active');
        let linkEndpoint = link.dataset.endpoint; // Relies on <a data-endpoint="page_name_endpoint">...</a>
        if (linkEndpoint === activePage) {
            link.classList.add('active');
        }
    });
    
    // Fallback for index/home page if no specific endpoint matches or for root path
    if (activePage === 'home_page' || (activePage === 'index' && (window.location.pathname === '/' || window.location.pathname.endsWith('/index.html')))){
        // Attempt to find home link by common patterns if specific data-endpoint isn't matched
        const homeLink = document.querySelector('.main-nav ul li a[data-endpoint="home_page"], .main-nav ul li a[href="index.html"], .main-nav ul li a[href="/"]');
        if(homeLink && !homeLink.classList.contains('active')) {
            // Deactivate others first if any got activated by mistake
            navLinks.forEach(l => l.classList.remove('active'));
            homeLink.classList.add('active');
        }
    }

    // Intersection Observer for fade-in-up animations
    // Uses class .animate-fadeInUp which should be defined in Tailwind config or style.css
    const animatedElements = document.querySelectorAll('.fade-in-up');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fadeInUp');
                // observer.unobserve(entry.target); // Unobserve after animation to prevent re-triggering
            } else {
                // Optional: Remove class if you want animation to replay on scroll back into view
                // entry.target.classList.remove('animate-fadeInUp'); 
            }
        });
    }, { threshold: 0.1 }); // Trigger when 10% of the element is visible

    animatedElements.forEach(el => {
        observer.observe(el);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const hrefAttribute = this.getAttribute('href');
            if (hrefAttribute.length > 1 && hrefAttribute.startsWith('#') && document.querySelector(hrefAttribute)) {
                e.preventDefault();
                document.querySelector(hrefAttribute).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

});
