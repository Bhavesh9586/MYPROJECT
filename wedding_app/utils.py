import random
import pyotp
from datetime import datetime, timedelta
from twilio.rest import Client
from django.conf import settings

def generate_otp():
    """Generate a 6-digit OTP code"""
    return str(random.randint(100000, 999999))

def send_otp_sms(phone_number, otp):
    """Send OTP via SMS"""
    try:
        # Check if Twilio credentials are configured
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
            # Send actual SMS via Twilio
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f'Your Prince Graphics verification code is: {otp}',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            print(f"SMS sent to {phone_number} with message ID: {message.sid}")
            return True
        else:
            # Development mode - print to console
            print(f"\n==============================================================")
            print(f"DEVELOPMENT MODE: OTP for {phone_number} is: {otp}")
            print(f"==============================================================\n")
            print("To send real SMS, configure TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in settings.py")
            return True
    except Exception as e:
        print(f"SMS sending error: {e}")
        return False

def is_otp_valid(otp_obj, otp_entered):
    """Check if OTP is valid and not expired (valid for 10 minutes)"""
    if not otp_obj:
        return False
        
    expiry_time = otp_obj.created_at + timedelta(minutes=10)
    if datetime.now().replace(tzinfo=expiry_time.tzinfo) > expiry_time:
        return False
        
    if otp_obj.otp != otp_entered:
        return False
        
    if otp_obj.count >= 5:  # Limit attempts to 5
        return False
        
    return True
