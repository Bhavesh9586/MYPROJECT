from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from django.utils import timezone

from .models import (
    WeddingDetails, InvitationTemplate, Event, 
    GalleryImage, Guest, ContactMessage, Testimonial, Category,
    UserProfile, CartItem, Order, OrderItem, PhoneOTP
)
from .forms import (
    ContactForm, RSVPForm, LoginForm, RegisterForm, 
    AddToCartForm, UserProfileUpdateForm, ProfileUpdateForm,
    CheckoutForm, PhoneVerificationForm, VerifyOTPForm
)
from .utils import generate_otp, send_otp_sms, is_otp_valid


def home(request):
    """Home page view"""
    try:
        wedding_details = WeddingDetails.objects.latest('id')
    except WeddingDetails.DoesNotExist:
        wedding_details = None
    
    events = Event.objects.all()[:3]
    gallery_images = GalleryImage.objects.all()[:6]
    testimonials = Testimonial.objects.filter(is_featured=True)[:3]
    
    context = {
        'wedding_details': wedding_details,
        'events': events,
        'gallery_images': gallery_images,
        'testimonials': testimonials,
    }
    return render(request, 'wedding_app/home.html', context)


def about(request):
    """About the couple page"""
    try:
        wedding_details = WeddingDetails.objects.latest('id')
    except WeddingDetails.DoesNotExist:
        wedding_details = None
    
    context = {
        'wedding_details': wedding_details,
    }
    return render(request, 'wedding_app/about.html', context)


def events(request):
    """Wedding events page"""
    events_list = Event.objects.all()
    
    context = {
        'events': events_list,
    }
    return render(request, 'wedding_app/events.html', context)


def gallery(request):
    """Photo gallery page with category filtering"""
    # Get all categories for filter sidebar
    categories = Category.objects.all()
    
    # Get selected category from query params
    category_slug = request.GET.get('category')
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 5000)
    formats = request.GET.getlist('format', [])
    
    # Base queryset
    images = GalleryImage.objects.all()
    
    # Apply filters
    if category_slug:
        images = images.filter(category__slug=category_slug)
    
    if min_price and max_price:
        images = images.filter(price__gte=min_price, price__lte=max_price)
    
    if formats:
        # Filter for any format that contains at least one of the requested formats
        # This is a simple approach - for more precise filtering you might need a M2M relationship
        format_filters = []
        for format_type in formats:
            format_filters.append(models.Q(formats__icontains=format_type))
        
        if format_filters:
            from django.db.models import Q
            format_query = format_filters.pop()
            for item in format_filters:
                format_query |= item
            images = images.filter(format_query)
    
    # Count images per category for sidebar
    category_counts = {}
    for category in categories:
        category_counts[category.slug] = GalleryImage.objects.filter(category=category).count()
    
    # Get format counts
    format_types = {'PSD': 0, 'Canva': 0, 'PDF': 0}
    for img in GalleryImage.objects.all():
        for fmt in format_types.keys():
            if fmt.lower() in img.formats.lower():
                format_types[fmt] += 1
    
    # Pagination
    paginator = Paginator(images, 12)  # Show 12 images per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'category_counts': category_counts,
        'format_types': format_types,
        'current_category': category_slug,
        'min_price': min_price,
        'max_price': max_price,
        'selected_formats': formats,
    }
    return render(request, 'wedding_app/gallery.html', context)


def invitation_preview(request, template_id):
    """Preview a specific invitation template"""
    template = get_object_or_404(InvitationTemplate, id=template_id, is_active=True)
    
    try:
        wedding_details = WeddingDetails.objects.latest('id')
    except WeddingDetails.DoesNotExist:
        wedding_details = None
    
    context = {
        'template': template,
        'wedding_details': wedding_details,
    }
    return render(request, 'wedding_app/invitation_preview.html', context)


def product_detail(request, product_id):
    """View a specific product/invitation design"""
    product = get_object_or_404(GalleryImage, id=product_id)
    related_products = GalleryImage.objects.filter(category=product.category).exclude(id=product_id)[:4]
    
    # Handle adding to cart
    if request.method == 'POST' and request.user.is_authenticated:
        form = AddToCartForm(request.POST)
        if form.is_valid():
            cart_item = form.save(commit=False)
            cart_item.user = request.user
            cart_item.gallery_image = product
            
            # Check if this item already exists in cart
            existing_item = CartItem.objects.filter(
                user=request.user,
                gallery_image=product,
                format=cart_item.format
            ).first()
            
            if existing_item:
                existing_item.quantity += cart_item.quantity
                existing_item.save()
                messages.success(request, "Cart updated successfully!")
            else:
                cart_item.save()
                messages.success(request, "Item added to cart!")
                
            return redirect('cart')
    else:
        form = AddToCartForm()
    
    context = {
        'product': product,
        'related_products': related_products,
        'form': form
    }
    return render(request, 'wedding_app/product_detail.html', context)


def rsvp(request):
    """RSVP form for guests"""
    if request.method == 'POST':
        form = RSVPForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            
            # Check if guest exists
            try:
                guest = Guest.objects.get(email=email)
                guest.rsvp_status = form.cleaned_data['rsvp_status']
                guest.plus_one = form.cleaned_data['plus_one']
                guest.plus_one_name = form.cleaned_data['plus_one_name']
                guest.dietary_restrictions = form.cleaned_data['dietary_restrictions']
                guest.save()
                messages.success(request, f"Thank you, {name}! Your RSVP has been updated.")
            except Guest.DoesNotExist:
                form.save()
                messages.success(request, f"Thank you, {name}! Your RSVP has been submitted.")
            
            return redirect('rsvp_success')
    else:
        form = RSVPForm()
    
    context = {
        'form': form
    }
    return render(request, 'wedding_app/rsvp.html', context)


def rsvp_success(request):
    """RSVP success page"""
    return render(request, 'wedding_app/rsvp_success.html')


def contact(request):
    """Contact form page"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent! We'll get back to you soon.")
            return redirect('contact_success')
    else:
        form = ContactForm()
    
    context = {
        'form': form
    }
    return render(request, 'wedding_app/contact.html', context)


def contact_success(request):
    """Contact form success page"""
    return render(request, 'wedding_app/contact_success.html')


def testimonials(request):
    """Client testimonials page"""
    testimonials_list = Testimonial.objects.all()
    
    context = {
        'testimonials': testimonials_list
    }
    return render(request, 'wedding_app/testimonials.html', context)


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'home')
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    
    context = {
        'form': form
    }
    return render(request, 'wedding_app/login.html', context)


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


def user_register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Prince Graphics, {user.first_name}! Your account has been created successfully.")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    
    context = {
        'form': form
    }
    return render(request, 'wedding_app/register.html', context)


@login_required
def profile(request):
    """User profile view"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user)
    
    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    else:
        user_form = UserProfileUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=user_profile)
    
    context = {
        'user_profile': user_profile,
        'user_form': user_form,
        'profile_form': profile_form,
        'orders': orders,
        'addresses': []  # Placeholder for future address functionality
    }
    return render(request, 'wedding_app/profile.html', context)


@login_required
def cart(request):
    """Shopping cart view"""
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Calculate totals
    subtotal = sum(item.get_total() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal
    }
    return render(request, 'wedding_app/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    """Add item to cart AJAX view"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product = get_object_or_404(GalleryImage, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        format_type = request.POST.get('format', 'PSD')
        
        # Check if this item already exists in cart
        existing_item = CartItem.objects.filter(
            user=request.user,
            gallery_image=product,
            format=format_type
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
        else:
            CartItem.objects.create(
                user=request.user,
                gallery_image=product,
                quantity=quantity,
                format=format_type
            )
        
        # Get updated cart count
        cart_count = CartItem.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Item added to cart successfully!',
            'cart_count': cart_count
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    }, status=400)


@login_required
def update_cart(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Item removed from cart',
                'removed': True
            })
        else:
            cart_item.quantity = quantity
            cart_item.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Cart updated',
                'total': float(cart_item.get_total()),
                'subtotal': float(sum(item.get_total() for item in CartItem.objects.filter(user=request.user)))
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    }, status=400)


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart!")
    return redirect('cart')


@login_required
def checkout(request):
    """Checkout process"""
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('gallery')
    
    # Calculate totals
    subtotal = sum(item.get_total() for item in cart_items)
    
    # Get user profile information
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = Order.objects.create(
                user=request.user,
                order_number=get_random_string(10).upper(),
                total_amount=subtotal,
                shipping_address={
                    'full_name': f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}",
                    'address': form.cleaned_data['address'],
                    'city': form.cleaned_data['city'],
                    'state': form.cleaned_data['state'],
                    'country': form.cleaned_data['country'],
                    'zip_code': form.cleaned_data['zip_code'],
                    'phone': form.cleaned_data['phone']
                },
                payment_method=form.cleaned_data['payment_method'],
                order_notes=form.cleaned_data.get('order_notes', ''),
                status='processing'
            )
            
            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    gallery_image=item.gallery_image,
                    quantity=item.quantity,
                    price=item.gallery_image.discount_price if item.gallery_image.discount_price else item.gallery_image.price,
                    format=item.format
                )
            
            # Clear cart
            cart_items.delete()
            
            # Prepare WhatsApp notification
            send_order_whatsapp_notification(order, form.cleaned_data)
            
            messages.success(request, f"Order #{order.order_number} placed successfully!")
            return redirect('order_confirmation', order_id=order.id)
    else:
        # Pre-fill form with user information
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': user_profile.phone,
            'address': user_profile.address,
            'country': 'India',  # Default country
        }
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'form': form
    }
    return render(request, 'wedding_app/checkout.html', context)


def send_order_whatsapp_notification(order, form_data):
    """Send order details to admin via WhatsApp"""
    # Build order message
    order_items = OrderItem.objects.filter(order=order)
    
    # Base URL for the site
    from django.contrib.sites.shortcuts import get_current_site
    from django.http import HttpRequest
    request = HttpRequest()
    request.META['HTTP_HOST'] = 'localhost:8000'  # Default for local development
    base_url = f"http://{get_current_site(request)}"
    
    # Format order details
    items_details = []
    image_links = []
    for item in order_items:
        item_detail = f"• {item.gallery_image.title} ({item.format}) × {item.quantity} = ₹{item.price * item.quantity}"
        items_details.append(item_detail)
        
        # Add image URL
        if item.gallery_image.image:
            image_url = f"{base_url}{item.gallery_image.image.url}"
            image_links.append(f"*Image for {item.gallery_image.title}:* {image_url}")
    
    message = f"""
*NEW ORDER #{order.order_number}*

*Customer Details:*
Name: {form_data['first_name']} {form_data['last_name']}
Email: {form_data['email']}
Phone: {form_data['phone']}

*Shipping Address:*
{form_data['address']}
{form_data['city']}, {form_data['state']} {form_data['zip_code']}
{form_data['country']}

*Order Items:*
{chr(10).join(items_details)}

*Product Images:*
{chr(10).join(image_links)}

*Total Amount: ₹{order.total_amount}*
Payment Method: {form_data['payment_method']}

*Order Notes:*
{form_data.get('order_notes', 'None')}
"""
    
    # Format WhatsApp URL with admin phone number (9484863965)
    admin_phone = "9484863965"
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://api.whatsapp.com/send?phone={admin_phone}&text={encoded_message}"
    
    # For demonstration purposes, we'll return the URL
    # In a production environment, you might use a WhatsApp Business API
    return whatsapp_url


@login_required
def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    # Generate WhatsApp link for admin notification
    whatsapp_link = generate_whatsapp_notification(order, order_items)
    
    context = {
        'order': order,
        'order_items': order_items,
        'whatsapp_link': whatsapp_link
    }
    return render(request, 'wedding_app/order_confirmation.html', context)


def generate_whatsapp_notification(order, order_items):
    """Generate WhatsApp notification link with order details"""
    # Format order details
    items_details = []
    image_links = []
    
    # Base URL for the site
    from django.contrib.sites.shortcuts import get_current_site
    from django.http import HttpRequest
    import json
    
    # Handle shipping_address - convert from string to dict if needed
    try:
        if isinstance(order.shipping_address, str):
            shipping_address = json.loads(order.shipping_address)
        else:
            shipping_address = order.shipping_address
    except json.JSONDecodeError:
        # If shipping_address is not valid JSON, use it as a plain string
        shipping_address = {"address": order.shipping_address}
    
    request = HttpRequest()
    request.META['HTTP_HOST'] = 'localhost:8000'  # Default for local development
    base_url = f"http://{get_current_site(request)}"
    
    for item in order_items:
        item_detail = f"• {item.gallery_image.title} ({item.format}) × {item.quantity} = ₹{item.price * item.quantity}"
        items_details.append(item_detail)
        
        # Add image URL
        if item.gallery_image.image:
            image_url = f"{base_url}{item.gallery_image.image.url}"
            image_links.append(f"*Image for {item.gallery_image.title}:* {image_url}")
    
    message = f"""
*NEW ORDER #{order.order_number}*

*Customer Details:*
Name: {order.user.get_full_name()}
Email: {order.user.email}
Phone: {shipping_address.get('phone', 'N/A')}

*Shipping Address:*
{shipping_address.get('address', 'N/A')}
{shipping_address.get('city', 'N/A')}, {shipping_address.get('state', 'N/A')} {shipping_address.get('zip_code', 'N/A')}
{shipping_address.get('country', 'N/A')}

*Order Items:*
{chr(10).join(items_details)}

*Product Images:*
{chr(10).join(image_links)}

*Total Amount: ₹{order.total_amount}*
Payment Method: {order.payment_method}

*Order Notes:*
{order.order_notes or 'None'}
"""
    
    # Format WhatsApp URL with admin phone number (9484863965)
    admin_phone = "9484863965"
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://api.whatsapp.com/send?phone={admin_phone}&text={encoded_message}"
    
    return whatsapp_url


# Security related views
def lockout(request):
    """View for displaying the account lockout page"""
    return render(request, 'wedding_app/lockout.html')


@login_required
def change_password(request):
    """Secure password change view"""
    from .forms import PasswordChangeSecureForm
    from django.contrib.auth import update_session_auth_hash
    
    if request.method == 'POST':
        form = PasswordChangeSecureForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            # Log the password change event
            import logging
            logger = logging.getLogger('django.security.auth')
            logger.info(f'Password changed successfully for user {request.user.username}')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeSecureForm(request.user)
    
    return render(request, 'wedding_app/change_password.html', {
        'form': form
    })


def error_403(request, exception=None):
    """Custom 403 forbidden error page"""
    return render(request, 'wedding_app/errors/403.html', status=403)


def error_404(request, exception=None):
    """Custom 404 not found error page"""
    return render(request, 'wedding_app/errors/404.html', status=404)


def error_500(request):
    """Custom 500 server error page"""
    return render(request, 'wedding_app/errors/500.html', status=500)
