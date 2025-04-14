/**
 * Main JavaScript file for Victory Invitations website
 */

// Wait for document to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize navbar scroll effect
    initNavbarScroll();
    
    // Initialize animation on scroll
    initAnimationOnScroll();
    
    // Auto hide alert messages
    initAlertAutoHide();
});

/**
 * Navbar scroll effect - change navbar appearance on scroll
 */
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled', 'shadow-sm');
            } else {
                navbar.classList.remove('navbar-scrolled', 'shadow-sm');
            }
        });
        
        // Trigger scroll event on page load to set initial state
        window.dispatchEvent(new Event('scroll'));
    }
}

/**
 * Initialize animation on scroll
 * Adds fade-in effect to elements as they come into view
 */
function initAnimationOnScroll() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length > 0) {
        // Initial check for elements in viewport
        checkIfInView();
        
        // Check elements on scroll
        window.addEventListener('scroll', checkIfInView);
    }
    
    function checkIfInView() {
        const windowHeight = window.innerHeight;
        const windowTopPosition = window.scrollY;
        const windowBottomPosition = windowTopPosition + windowHeight;
        
        animatedElements.forEach(function(element) {
            const elementHeight = element.offsetHeight;
            const elementTopPosition = getOffsetTop(element);
            const elementBottomPosition = elementTopPosition + elementHeight;
            
            // Check if element is in viewport
            if (
                elementBottomPosition >= windowTopPosition && 
                elementTopPosition <= windowBottomPosition
            ) {
                element.classList.add('animated');
            }
        });
    }
    
    // Helper function to get element's offset top position
    function getOffsetTop(element) {
        let offsetTop = 0;
        while(element) {
            offsetTop += element.offsetTop;
            element = element.offsetParent;
        }
        return offsetTop;
    }
}

/**
 * Auto hide alert messages after 5 seconds
 */
function initAlertAutoHide() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Create fade out effect
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            
            // Remove alert after fade out
            setTimeout(function() {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 500);
        }, 5000);
    });
}

/**
 * Gallery image filtering
 */
function filterGallery(category) {
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    galleryItems.forEach(function(item) {
        const itemCategories = item.getAttribute('data-category').split(' ');
        
        if (category === 'all' || itemCategories.includes(category)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}
