from django.urls import path
from . import views

urlpatterns = [
    # Main Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('gallery/', views.gallery, name='gallery'),
    path('invitation/<int:template_id>/', views.invitation_preview, name='invitation_preview'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('testimonials/', views.testimonials, name='testimonials'),
    
    # RSVP
    path('rsvp/', views.rsvp, name='rsvp'),
    path('rsvp/success/', views.rsvp_success, name='rsvp_success'),
    
    # Contact
    path('contact/', views.contact, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('locked-out/', views.lockout, name='lockout'),
    
    # Shopping Cart
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    # Security
    path('403/', views.error_403, name='error_403'),
    path('404/', views.error_404, name='error_404'),
    path('500/', views.error_500, name='error_500'),
]
