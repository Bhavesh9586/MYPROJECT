import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wedding_project.settings')
django.setup()

from django.contrib.auth.models import User
from wedding_app.models import GalleryImage, CartItem

# Get the first user and gallery image
user = User.objects.first()
gallery_image = GalleryImage.objects.first()

if user and gallery_image:
    # Create a test cart item
    cart_item = CartItem(
        user=user,
        gallery_image=gallery_image,
        quantity=3,
        format='PSD'
    )
    cart_item.save()
    print(f"Created test cart item: {cart_item}")
    print(f"User: {user.username}")
    print(f"Product: {gallery_image.title}")
    print(f"Quantity: {cart_item.quantity}")
else:
    if not user:
        print("No users found in the database.")
    if not gallery_image:
        print("No gallery images found in the database.")
