from django.db import models
from django.contrib.auth.models import User


class WeddingDetails(models.Model):
    """Main wedding details including couple names, date, venue, etc."""
    bride_name = models.CharField(max_length=100)
    groom_name = models.CharField(max_length=100)
    wedding_date = models.DateField()
    wedding_time = models.TimeField()
    venue_name = models.CharField(max_length=200)
    venue_address = models.TextField()
    venue_map_link = models.URLField(blank=True, null=True)
    about_bride = models.TextField(blank=True, null=True)
    about_groom = models.TextField(blank=True, null=True)
    love_story = models.TextField(blank=True, null=True)
    main_image = models.ImageField(upload_to='wedding_images/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.bride_name} & {self.groom_name}'s Wedding"
    
    class Meta:
        verbose_name_plural = "Wedding Details"


class InvitationTemplate(models.Model):
    """Different invitation designs/templates available"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    preview_image = models.ImageField(upload_to='templates/', blank=True, null=True)
    html_content = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class Event(models.Model):
    """Different events during the wedding (ceremony, reception, etc.)"""
    title = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order', 'date', 'time']


class Category(models.Model):
    """Categories for invitation designs"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Categories"


class GalleryImage(models.Model):
    """Images for the wedding gallery"""
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='gallery_images')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=499.00)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    formats = models.CharField(max_length=200, default='PSD, Canva', help_text='Comma separated list of available formats')
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']


class Guest(models.Model):
    """Wedding guests information"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    invitation_sent = models.BooleanField(default=False)
    rsvp_status_choices = [
        ('pending', 'Pending'),
        ('attending', 'Attending'),
        ('not_attending', 'Not Attending'),
    ]
    rsvp_status = models.CharField(max_length=20, choices=rsvp_status_choices, default='pending')
    plus_one = models.BooleanField(default=False)
    plus_one_name = models.CharField(max_length=100, blank=True, null=True)
    dietary_restrictions = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    """Messages from the contact form"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name}: {self.subject}"
    
    class Meta:
        ordering = ['-created_at']


class Testimonial(models.Model):
    """Client testimonials for the business"""
    client_name = models.CharField(max_length=100)
    client_photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    wedding_date = models.DateField(blank=True, null=True)
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.client_name


class UserProfile(models.Model):
    """Extended user profile for customers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    
    def __str__(self):
        return self.user.username


class CartItem(models.Model):
    """Individual items in a user's cart"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    gallery_image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    format = models.CharField(max_length=50, default='PSD')
    added_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.gallery_image.title} ({self.quantity})"
    
    def get_total(self):
        """Calculate total price for this cart item"""
        if self.gallery_image.discount_price:
            return self.gallery_image.discount_price * self.quantity
        return self.gallery_image.price * self.quantity
    get_total.short_description = "Total Price"


class Order(models.Model):
    """Orders placed by users"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=50)
    payment_status = models.BooleanField(default=False)
    order_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.order_number
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Individual items within an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    gallery_image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    format = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.order.order_number} - {self.gallery_image.title}"


class PhoneOTP(models.Model):
    """Store OTP codes for phone verification"""
    phone = models.CharField(max_length=20)
    otp = models.CharField(max_length=6)
    count = models.IntegerField(default=0, help_text='Number of OTP attempts')
    validated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.phone} - {self.otp} - validated: {self.validated}"
