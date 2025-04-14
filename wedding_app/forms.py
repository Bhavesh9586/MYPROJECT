from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import ContactMessage, Guest, UserProfile, CartItem
import re


class SecurityMixin:
    """Mixin to add security features to forms"""
    
    def clean(self):
        """Validate form data for security threats"""
        cleaned_data = super().clean()
        
        # Check for potential XSS or SQL injection in text fields
        for field_name, field_value in cleaned_data.items():
            if isinstance(field_value, str):
                # Check for common XSS patterns
                xss_patterns = [
                    r'<script.*?>.*?</script>', 
                    r'javascript:', 
                    r'onerror=', 
                    r'onload=',
                    r'eval\(.*?\)',
                    r'document\.cookie'
                ]
                
                for pattern in xss_patterns:
                    if re.search(pattern, field_value, re.IGNORECASE):
                        self.add_error(field_name, "This field contains potentially harmful content.")
                
                # Check for SQL injection patterns
                sql_patterns = [
                    r'(\s|;)*(SELECT|INSERT|UPDATE|DELETE|DROP|UNION)(\s|;)+',
                    r'--.*$',
                    r'/\*.*\*/',
                    r'1=1',
                    r'OR 1=1'
                ]
                
                for pattern in sql_patterns:
                    if re.search(pattern, field_value, re.IGNORECASE):
                        self.add_error(field_name, "This field contains potentially harmful content.")
        
        return cleaned_data


class ContactForm(SecurityMixin, forms.ModelForm):
    """Form for contact messages"""
    honeypot = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'style': 'display:none !important'}),
        label="Leave this field empty"
    )
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        honeypot = cleaned_data.get('honeypot', '')
        
        # If honeypot field is filled, likely a bot
        if honeypot:
            raise forms.ValidationError("Bot detected. If you are not a bot, please try again.")
        
        return cleaned_data


class RSVPForm(SecurityMixin, forms.ModelForm):
    """Form for RSVP submissions"""
    rsvp_status = forms.ChoiceField(
        choices=[('attending', 'I will attend'), ('not_attending', 'I cannot attend')],
        widget=forms.RadioSelect(attrs={'class': 'custom-radio'})
    )
    
    class Meta:
        model = Guest
        fields = ['name', 'email', 'phone', 'rsvp_status', 'plus_one', 'plus_one_name', 'dietary_restrictions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Phone Number (Optional)'}),
            'plus_one': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'plus_one_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guest Name (if bringing a plus one)'}),
            'dietary_restrictions': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Any dietary restrictions or special requests?', 'rows': 3}),
        }


class LoginForm(SecurityMixin, AuthenticationForm):
    """Enhanced login form with Bootstrap styling and security features"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Username',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )
    
    error_messages = {
        'invalid_login': "Please enter a correct username and password. Note that both fields may be case-sensitive.",
        'inactive': "This account is inactive.",
    }
    
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )


class StrongPasswordValidator:
    """Custom password validator for strong passwords"""
    
    def validate(self, password, user=None):
        if len(password) < 10:
            raise forms.ValidationError("Password must be at least 10 characters long.")
        
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must contain at least one digit.")
        
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        
        if not any(char.islower() for char in password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        
        if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in password):
            raise forms.ValidationError("Password must contain at least one special character.")


class RegisterForm(SecurityMixin, UserCreationForm):
    """User registration form with additional fields and security features"""
    
    # Adding custom validators
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        max_length=254, 
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    phone = forms.CharField(
        max_length=20, 
        required=False,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (Optional)'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address (Optional)', 'rows': 3})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add password strength meter hint
        self.fields['password1'].help_text += " For a strong password, include uppercase and lowercase letters, numbers, and special characters."
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        validator = StrongPasswordValidator()
        try:
            validator.validate(password)
        except forms.ValidationError as error:
            self.add_error('password1', error)
        return password
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address']
            )
        
        return user


class PasswordChangeSecureForm(SecurityMixin, PasswordChangeForm):
    """Enhanced password change form with security features"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        validator = StrongPasswordValidator()
        try:
            validator.validate(password)
        except forms.ValidationError as error:
            self.add_error('new_password1', error)
        return password


class AddToCartForm(SecurityMixin, forms.ModelForm):
    """Form for adding items to cart"""
    format = forms.ChoiceField(
        choices=[('PSD', 'PSD File'), ('Canva', 'Canva Template'), ('PDF', 'PDF File')],
        widget=forms.RadioSelect(attrs={'class': 'format-radio'})
    )
    
    class Meta:
        model = CartItem
        fields = ['quantity', 'format']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10', 'value': '1'})
        }


class UserProfileUpdateForm(SecurityMixin, forms.ModelForm):
    """Form for updating user information"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileUpdateForm(SecurityMixin, forms.ModelForm):
    """Form for updating user profile information"""
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'profile_image']
        widgets = {
            'profile_image': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image:
            # Validate image size
            if image.size > 2 * 1024 * 1024:  # 2MB limit
                raise forms.ValidationError("Image file size should be less than 2MB.")
            
            # Validate file extension
            allowed_extensions = ['jpg', 'jpeg', 'png']
            ext = image.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(f"Only {', '.join(allowed_extensions)} files are allowed.")
        
        return image


class CheckoutForm(SecurityMixin, forms.Form):
    """Form for checkout process"""
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    zip_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('cod', 'Cash on Delivery')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    order_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


class PhoneVerificationForm(SecurityMixin, forms.Form):
    """Form for verifying phone number with OTP"""
    phone = forms.CharField(
        max_length=20,
        required=True,
        validators=[RegisterForm.phone_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'})
    )


class VerifyOTPForm(SecurityMixin, forms.Form):
    """Form for entering OTP code"""
    otp = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter OTP', 
            'type': 'number',
            'maxlength': '6',
            'minlength': '6'
        })
    )
    phone = forms.CharField(widget=forms.HiddenInput())
