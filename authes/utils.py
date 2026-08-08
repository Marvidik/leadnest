from django.core.mail import send_mail
from django.utils.html import format_html
import os
import random
import string
from django.contrib.auth.models import User
from user.email_service import BrevoEmailService
from user.models import ReferalBonus,ReferalList, UserProfile
from user.utils import update_user_account


def generate_numeric_otp(length=4):
    """Generate a random numeric OTP of given length (default: 6 digits)."""
    return ''.join(random.choices(string.digits, k=length))



from django.template.loader import render_to_string
 
LOGO_URL = "https://res.cloudinary.com/dpuvtcctg/image/upload/v1782941110/5f1f92ad-e821-4512-b4b3-423f7021e1d4_nqqkfn.jpg"  # replace with your real logo URL
 
 
def send_welcome_mail(email, full_name, username, account_type, user_id):
    try:
        subject = "Welcome to Equinox Global Assets"
        message = f"""
        <p>Thank you for joining <strong>Equinox Global Assets</strong> — your new home for smart, secure, and rewarding investments.</p>
        <p>Here's a quick summary of your profile:</p>
        <table style="width:100%; border-collapse: collapse; margin-top: 16px; margin-bottom: 16px;">
            <tr>
                <td style="padding:10px; border:1px solid #eef0f2;"><strong>Username:</strong></td>
                <td style="padding:10px; border:1px solid #eef0f2;">{username}</td>
            </tr>
            <tr>
                <td style="padding:10px; border:1px solid #eef0f2;"><strong>Account Type:</strong></td>
                <td style="padding:10px; border:1px solid #eef0f2;">{account_type}</td>
            </tr>
        </table>
        <p>Verify your account with the link below:</p>
        <p>
            <a href="https://www.equinoxglobals.com/auth/verify-account?user_id={user_id}" class="btn">
                Click here to verify your account
            </a>
        </p>
        <p>We're excited to have you on board.</p>
        """
 
        html_content = render_to_string("emails/admin_broadcast.html", {
            "user_name": full_name,
            "subject": subject,
            "message": message,
            "logo_url": LOGO_URL,
        })
 
        BrevoEmailService.send_email(
            subject=subject,
            html_content=html_content,
            recipients=[email],
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {str(e)}")
        return False
 
 
def send_otp_mail(email, otp):
    try:
        subject = "OTP Request"
        message = f"""
        <p>You requested an <strong>OTP</strong> for your account.</p>
        <p>Your OTP is:</p>
        <h2 style="color:#14b8a6; letter-spacing: 4px;">{otp}</h2>
        <p>We're excited to have you on board.</p>
        """
 
        html_content = render_to_string("emails/admin_broadcast.html", {
            "user_name": "there",
            "subject": subject,
            "message": message,
            "logo_url": LOGO_URL,
        })
 
        BrevoEmailService.send_email(
            subject=subject,
            html_content=html_content,
            recipients=[email],
        )
        return True
    except Exception as e:
        print(f"Error sending OTP email: {str(e)}")
        return False


def process_referral(referee_username, new_user, bonus_amount=5):
    if not referee_username:
        return False
        
    try:
        referee = User.objects.get(username=referee_username)
        
        # Create referral bonus for the referee
        ReferalBonus.objects.create(
            user=referee,
            amount=bonus_amount
        )
        
       

        

        # Create referral list entry
        ReferalList.objects.create(
            user= referee,
            client_name=new_user.username,
            ref_level=1,
            client_status="registered"
        )
        
        user= User.objects.filter(username=referee_username).first()

        update_user_account(user)

        return True
        
    except User.DoesNotExist:
        # Log this if needed: referee doesn't exist
        return False
    except Exception as e:
        # Log the error if needed
        return False