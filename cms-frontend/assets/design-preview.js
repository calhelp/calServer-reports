(function () {
  const slider = document.querySelector('[data-preview-slider]');
  const dotsHost = document.querySelector('[data-slider-dots]');
  if (!slider || !dotsHost) return;

  const items = Array.from(slider.querySelectorAll('[data-slider-item]'));
  let activeIndex = 0;

  const setActive = (index) => {
    activeIndex = index;
    items.forEach((item, i) => {
      item.style.display = i === index ? 'block' : 'none';
      item.classList.toggle('is-visible', i === index);
    });
    dotsHost.querySelectorAll('.design-preview__dot').forEach((dot, i) => {
      dot.setAttribute('aria-current', i === index);
    });
  };

  const buildDots = () => {
    dotsHost.innerHTML = '';
    items.forEach((_, idx) => {
      const btn = document.createElement('button');
      btn.className = 'design-preview__dot';
      btn.type = 'button';
      btn.setAttribute('aria-label', `Slide ${idx + 1}`);
      btn.addEventListener('click', () => setActive(idx));
      dotsHost.appendChild(btn);
    });
  };

  const setupScrollReveal = () => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
          }
        });
      },
      { threshold: 0.12 }
    );

    document
      .querySelectorAll('.design-preview__card, .design-preview__section')
      .forEach((element) => observer.observe(element));
  };

  buildDots();
  setActive(activeIndex);
  setupScrollReveal();
})();
