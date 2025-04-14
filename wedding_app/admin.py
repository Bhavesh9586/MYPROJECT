from django.contrib import admin
from django.utils.html import format_html
from .models import (
    GalleryImage, Guest, ContactMessage,
    CartItem, Order, OrderItem, UserProfile
)

# Create a base admin class that uses our lightbox template
class LightboxAdminMixin:
    change_form_template = 'admin/image_lightbox.html'
    change_list_template = 'admin/image_lightbox.html'

class GalleryImageAdmin(LightboxAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'display_image')
    list_filter = ('category',)
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="auto" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Image'

class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'read')
    list_filter = ('read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'display_image', 'gallery_image', 'quantity', 'format')
    
    def display_image(self, obj):
        if obj.gallery_image and obj.gallery_image.image:
            return format_html('<img src="{}" width="80" height="auto" />', obj.gallery_image.image.url)
        return "No Image"
    display_image.short_description = 'Product Image'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('display_image', 'gallery_image', 'quantity', 'price', 'format')
    fields = ('display_image', 'gallery_image', 'quantity', 'price', 'format')
    
    def display_image(self, obj):
        if obj.gallery_image and obj.gallery_image.image:
            return format_html('<img src="{}" width="80" height="auto" />', obj.gallery_image.image.url)
        return "No Image"
    display_image.short_description = 'Product Image'

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'status', 'payment_method')
    list_filter = ('status', 'payment_method')
    inlines = [OrderItemInline]

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')

# Register models
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(GalleryImage, GalleryImageAdmin)
admin.site.register(Guest, GuestAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

# Customize admin panel
admin.site.site_header = "Prince Graphics Admin"
admin.site.site_title = "Prince Graphics Admin Portal"
admin.site.index_title = "Welcome to Prince Graphics Manager"
