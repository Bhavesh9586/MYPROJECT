from .models import CartItem

def cart_processor(request):
    """
    Context processor to add cart count to all templates
    """
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    
    return {
        'cart_count': cart_count
    }
