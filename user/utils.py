from django.db.models import Sum
from .models import UserAccount, Deposit, Bonus, ReferalBonus, Withdrawal,Profit,Penalty,UserInvestment
from django.core.mail import send_mail
from django.utils.html import format_html
import os
from django.utils.timezone import now,timedelta
from .email_service import BrevoEmailService


def update_user_account(user):
    # Aggregate deposit (only confirmed)
    total_deposit = Deposit.objects.filter(user=user, status=True).aggregate(total=Sum('amount'))['total'] or 0

    # Aggregate withdrawal
    total_withdrawal = Withdrawal.objects.filter(user=user,status=True).aggregate(total=Sum('amount'))['total'] or 0

    # Aggregate bonuses
    bonus = Bonus.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    penalty = Penalty.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    referal_bonus = ReferalBonus.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0

    total_profit = Profit.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    # Calculate profit and balance
    investment=UserInvestment.objects.filter(user=user,is_active=True,matured=False).aggregate(total=Sum('amount'))['total'] or 0

    account_balance = total_deposit + total_profit + bonus + referal_bonus - total_withdrawal - penalty - investment

    # Update the UserAccount
    account, created = UserAccount.objects.get_or_create(user=user)
    account.account_balance = account_balance
    account.total_profit = total_profit
    account.bonus = bonus
    account.referal_bonus = referal_bonus
    account.total_deposit = total_deposit
    account.total_withdrawal = total_withdrawal
    account.save()


def process_matured_investments():
    matured_count = 0
    reinvested_count = 0

    investments = UserInvestment.objects.filter(is_active=True, end_date__lte=now())

    for investment in investments:
        profit_amount = int((investment.amount * investment.plan.profit_percent) / 100)

        # Mark as matured
        investment.matured = True
        investment.is_active = False
        investment.profit_earned = profit_amount
        investment.save()

        # Create profit record
        Profit.objects.create(
            user=investment.user,
            plan=investment.plan.name,
            amount=profit_amount,
            type="profit"
        )
        matured_count += 1

        # Auto reinvest if enabled
        if investment.auto_reinvest:
            new_start = investment.end_date
            new_end = new_start + timedelta(hours=investment.plan.duration)

            UserInvestment.objects.create(
                user=investment.user,
                plan=investment.plan,
                amount=investment.amount,
                type="investment",
                auto_reinvest=True,
                start_date=new_start,
                end_date=new_end
            )

            reinvested_count += 1

    return {"matured": matured_count, "reinvested": reinvested_count}

from django.template.loader import render_to_string

LOGO_URL = "https://res.cloudinary.com/ds2ya2dzu/image/upload/v1790278951/WhatsApp_Image_2025-09-28_at_08.28.11_ebf69e75_khdgvx.jpg"  # replace with your real logo URL


def send_deposit_mail(email, amount, user_name=None):
    try:
        subject = "Deposit Request"
        message = f"""
        <p>You submitted a <strong>Deposit</strong> request for your account.</p>
        <p><strong>Amount:</strong> ${amount}</p>
        <p>Your request has been received and will be processed shortly.</p>
        """

        html_content = render_to_string("emails/admin_broadcast.html", {
            "user_name": user_name or "there",
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
        print(f"Error sending deposit email: {str(e)}")
        return False


def send_withdrawal_mail(email, amount, user_name=None):
    try:
        subject = "Withdrawal Request"
        message = f"""
        <p>You submitted a <strong>Withdrawal</strong> request for your account.</p>
        <p><strong>Amount:</strong> ${amount}</p>
        <p>Your request has been received and will be processed shortly.</p>
        """

        html_content = render_to_string("emails/admin_broadcast.html", {
            "user_name": user_name or "there",
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
        print(f"Error sending withdrawal email: {str(e)}")
        return False


def send_Trading_mail(email, amount, plan, user_name=None):
    try:
        subject = "Trade"
        message = f"""
        <p>You started a <strong>{plan} Trade</strong> in your account.</p>
        <p><strong>Amount:</strong> ${amount}</p>
        <p>Your trade profit will be calculated and credited to you after due time.</p>
        """

        html_content = render_to_string("emails/admin_broadcast.html", {
            "user_name": user_name or "there",
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
        print(f"Error Trading email: {str(e)}")
        return False


def send_admin_broadcast_email(user, subject, message):
    try:
        html_content = render_to_string("emails/admin_broadcast.html", {
            "user_name": getattr(user, "first_name", None) or getattr(user, "username", None) or "there",
            "message": message,
            "logo_url": LOGO_URL,
        })

        BrevoEmailService.send_email(
            subject=subject,
            html_content=html_content,
            recipients=[user.email],
        )
        return True
    except Exception as e:
        print(f"Error sending admin broadcast email to {user.email}: {str(e)}")
        return False