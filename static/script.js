// Wait for DOM to be fully loaded
document.addEventListener("DOMContentLoaded", () => {
  // Mobile menu toggle
  const menuToggle = document.querySelector(".menu-toggle")
  const nav = document.querySelector("nav")

  if (menuToggle && nav) {
    menuToggle.addEventListener("click", () => {
      nav.classList.toggle("active")

      // Animate hamburger to X
      const bars = document.querySelectorAll(".bar")
      bars[0].style.transform = nav.classList.contains("active") ? "rotate(45deg) translate(6px, 6px)" : ""
      bars[1].style.opacity = nav.classList.contains("active") ? "0" : "1"
      bars[2].style.transform = nav.classList.contains("active") ? "rotate(-45deg) translate(6px, -6px)" : ""
    })
  }

  // Testimonial slider
  const testimonials = document.querySelectorAll(".testimonial")
  const dots = document.querySelectorAll(".dot")
  let currentTestimonial = 0

  // Function to change testimonial
  function changeTestimonial(index) {
    // Hide all testimonials
    testimonials.forEach((testimonial) => {
      testimonial.classList.remove("active")
    })

    // Deactivate all dots
    dots.forEach((dot) => {
      dot.classList.remove("active")
    })

    // Show selected testimonial and activate dot
    testimonials[index].classList.add("active")
    dots[index].classList.add("active")

    // Update current index
    currentTestimonial = index
  }

  // Add click event to dots
  dots.forEach((dot) => {
    dot.addEventListener("click", function () {
      const index = Number.parseInt(this.getAttribute("data-index"))
      changeTestimonial(index)
    })
  })

  // Auto-rotate testimonials
  if (testimonials.length > 0) {
    setInterval(() => {
      const nextIndex = (currentTestimonial + 1) % testimonials.length
      changeTestimonial(nextIndex)
    }, 5000)
  }

  // Animate service cards on scroll
  const serviceCards = document.querySelectorAll(".service-card")
  const projectCards = document.querySelectorAll(".project-card")

  // Simple animation on scroll function
  function animateOnScroll(elements, className = "animate") {
    if (!elements.length) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setTimeout(() => {
              entry.target.classList.add(className)
            }, 150 * Array.from(elements).indexOf(entry.target))
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.2 },
    )

    elements.forEach((element) => {
      observer.observe(element)
    })
  }

  // Add CSS for animations
  const style = document.createElement("style")
  style.textContent = `
        .service-card, .project-card {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        }
        
        .service-card.animate, .project-card.animate {
            opacity: 1;
            transform: translateY(0);
        }
    `
  document.head.appendChild(style)

  // Initialize animations
  animateOnScroll(serviceCards)
  animateOnScroll(projectCards)


  const navLinks = document.querySelectorAll("nav a")

  navLinks.forEach((link) => {
    link.addEventListener("click", function (e) {

      if (this.getAttribute("href").startsWith("#")) {
        e.preventDefault()

        const targetId = this.getAttribute("href")
        const targetElement = document.querySelector(targetId)

        if (targetElement) {

          if (nav.classList.contains("active")) {
            nav.classList.remove("active")
            const bars = document.querySelectorAll(".bar")
            bars[0].style.transform = ""
            bars[1].style.opacity = "1"
            bars[2].style.transform = ""
          }


          window.scrollTo({
            top: targetElement.offsetTop - 80,
            behavior: "smooth",
          })
        }
      }
    })
  })
})
