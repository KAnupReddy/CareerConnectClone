/**
 * CareerConnect Clone - Frontend Interactions & Accessibility
 * Handles theme toggle, mobile sheet drawer, FAQ accordions,
 * back-to-top button, form duplicate prevention, and lightbox modals.
 */

document.addEventListener('DOMContentLoaded', () => {
  // --------------------------------------------------------------------------
  // 1. Theme Management (Light / Dark Mode)
  // --------------------------------------------------------------------------
  const themeToggleButtons = document.querySelectorAll('.theme-toggle');
  const storedTheme = localStorage.getItem('theme');

  const applyTheme = (theme) => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
      themeToggleButtons.forEach(btn => btn.setAttribute('aria-label', 'Switch to light theme'));
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
      themeToggleButtons.forEach(btn => btn.setAttribute('aria-label', 'Switch to dark theme'));
    }
  };

  // Initial theme initialization: default to dark as reference site displays
  if (storedTheme) {
    applyTheme(storedTheme);
  } else {
    applyTheme('dark');
  }

  themeToggleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const isDark = document.documentElement.classList.contains('dark');
      applyTheme(isDark ? 'light' : 'dark');
    });
  });

  // --------------------------------------------------------------------------
  // 2. Mobile Drawer Navigation
  // --------------------------------------------------------------------------
  const mobileMenuOpenBtn = document.getElementById('mobile-menu-open');
  const mobileMenuCloseBtn = document.getElementById('mobile-menu-close');
  const mobileDrawer = document.getElementById('mobile-drawer');
  const mobileOverlay = document.getElementById('mobile-drawer-overlay');

  const openMobileMenu = () => {
    if (mobileDrawer && mobileOverlay) {
      mobileDrawer.classList.add('active');
      mobileOverlay.classList.add('active');
      mobileDrawer.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      if (mobileMenuCloseBtn) mobileMenuCloseBtn.focus();
    }
  };

  const closeMobileMenu = () => {
    if (mobileDrawer && mobileOverlay) {
      mobileDrawer.classList.remove('active');
      mobileOverlay.classList.remove('active');
      mobileDrawer.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      if (mobileMenuOpenBtn) mobileMenuOpenBtn.focus();
    }
  };

  if (mobileMenuOpenBtn) mobileMenuOpenBtn.addEventListener('click', openMobileMenu);
  if (mobileMenuCloseBtn) mobileMenuCloseBtn.addEventListener('click', closeMobileMenu);
  if (mobileOverlay) mobileOverlay.addEventListener('click', closeMobileMenu);

  const drawerLinks = document.querySelectorAll('.mobile-drawer a');
  drawerLinks.forEach(link => {
    link.addEventListener('click', closeMobileMenu);
  });

  // --------------------------------------------------------------------------
  // 3. FAQ Accordion (Single-Collapsible Behavior)
  // --------------------------------------------------------------------------
  const accordionTriggers = document.querySelectorAll('.accordion-trigger');
  accordionTriggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
      const item = trigger.closest('.accordion-item');
      const content = item.querySelector('.accordion-content');
      const isExpanded = trigger.getAttribute('aria-expanded') === 'true';

      // Close all other open items
      document.querySelectorAll('.accordion-item').forEach(otherItem => {
        if (otherItem !== item) {
          const otherTrigger = otherItem.querySelector('.accordion-trigger');
          const otherContent = otherItem.querySelector('.accordion-content');
          if (otherTrigger) otherTrigger.setAttribute('aria-expanded', 'false');
          if (otherContent) {
            otherContent.style.maxHeight = null;
            otherContent.classList.remove('open');
          }
        }
      });

      // Toggle current item
      if (isExpanded) {
        trigger.setAttribute('aria-expanded', 'false');
        if (content) {
          content.style.maxHeight = null;
          content.classList.remove('open');
        }
      } else {
        trigger.setAttribute('aria-expanded', 'true');
        if (content) {
          content.classList.add('open');
          content.style.maxHeight = content.scrollHeight + 'px';
        }
      }
    });
  });

  // --------------------------------------------------------------------------
  // 4. Back-to-Top Button
  // --------------------------------------------------------------------------
  const backToTopBtn = document.getElementById('back-to-top');
  if (backToTopBtn) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 400) {
        backToTopBtn.classList.remove('hidden');
      } else {
        backToTopBtn.classList.add('hidden');
      }
    });

    backToTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, left: 0, behavior: 'smooth' });
    });
  }

  // --------------------------------------------------------------------------
  // 5. Flash Message Auto-Dismissal
  // --------------------------------------------------------------------------
  const toastAlerts = document.querySelectorAll('.toast');
  toastAlerts.forEach(toast => {
    setTimeout(() => {
      toast.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      setTimeout(() => toast.remove(), 500);
    }, 4500);
  });

  // --------------------------------------------------------------------------
  // 6. Form Submission Handling & Duplicate Prevention
  // --------------------------------------------------------------------------
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', (e) => {
      // Find submit button
      const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (!submitBtn) return;

      // Basic client-side validation
      const nameInput = form.querySelector('input[name="name"], input[name="full_name"]');
      const emailInput = form.querySelector('input[name="email"]');
      const messageInput = form.querySelector('textarea[name="message"]');

      if (nameInput && nameInput.value.trim().length < 2) {
        e.preventDefault();
        nameInput.focus();
        nameInput.classList.add('border-destructive');
        alert('Please enter a valid name (at least 2 characters).');
        return;
      }

      if (emailInput) {
        const emailPattern = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
        if (!emailPattern.test(emailInput.value.trim())) {
          e.preventDefault();
          emailInput.focus();
          emailInput.classList.add('border-destructive');
          alert('Please enter a valid email address.');
          return;
        }
      }

      if (messageInput && messageInput.value.trim().length < 5) {
        e.preventDefault();
        messageInput.focus();
        messageInput.classList.add('border-destructive');
        alert('Please enter a message of at least 5 characters.');
        return;
      }

      // Prevent duplicate submissions: disable button and show loading state
      submitBtn.disabled = true;
      submitBtn.classList.add('opacity-75', 'cursor-not-allowed');
      const originalText = submitBtn.textContent;
      submitBtn.innerHTML = `
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg> Submitting...
      `;

      // Allow form to submit naturally to Flask backend
    });
  });

  // --------------------------------------------------------------------------
  // 7. Testimonial Lightbox Modal
  // --------------------------------------------------------------------------
  const modalOverlay = document.getElementById('image-modal-overlay');
  const modalImg = document.getElementById('image-modal-img');
  const modalCloseBtn = document.getElementById('image-modal-close');
  const zoomableImages = document.querySelectorAll('.testimonial-zoomable');

  const openModal = (src, alt) => {
    if (modalOverlay && modalImg) {
      modalImg.src = src;
      modalImg.alt = alt || 'Preview';
      modalOverlay.classList.add('active');
      modalOverlay.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      if (modalCloseBtn) modalCloseBtn.focus();
    }
  };

  const closeModal = () => {
    if (modalOverlay) {
      modalOverlay.classList.remove('active');
      modalOverlay.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      if (modalImg) modalImg.src = '';
    }
  };

  zoomableImages.forEach(img => {
    img.addEventListener('click', () => openModal(img.src, img.alt));
    img.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openModal(img.src, img.alt);
      }
    });
  });

  if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeModal);
  if (modalOverlay) {
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) closeModal();
    });
  }

  // Global Escape key listener for open modals/drawers
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (modalOverlay && modalOverlay.classList.contains('active')) {
        closeModal();
      }
      if (mobileDrawer && mobileDrawer.classList.contains('active')) {
        closeMobileMenu();
      }
    }
  });
});
