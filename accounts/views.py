"""
Views for user registration, authentication, email verification, and profile management.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

from .forms import VoterRegistrationForm, VoterLoginForm, ProfileUpdateForm
from .models import VoterProfile, EmailVerificationToken


def register_view(request):
    """
    Handle voter registration with email verification.
    Creates a User, VoterProfile, and sends verification email.
    """
    if request.user.is_authenticated:
        return redirect('voter_dashboard')

    if request.method == 'POST':
        form = VoterRegistrationForm(request.POST)
        if form.is_valid():
            # Create user (inactive until email verified)
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Create voter profile
            VoterProfile.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                phone=form.cleaned_data.get('phone', ''),
                date_of_birth=form.cleaned_data.get('date_of_birth'),
            )

            # Create verification token and send email
            token = EmailVerificationToken.objects.create(user=user)
            _send_verification_email(user, token)

            messages.success(
                request,
                'Registration successful! Please check your email to verify your account.'
            )
            return redirect('login')
    else:
        form = VoterRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def _send_verification_email(user, token):
    """Send the verification email with a clickable link."""
    verification_url = f"{settings.SITE_URL}/accounts/verify/{token.token}/"
    subject = 'VoteSecure — Verify Your Email Address'
    html_message = f"""
    <div style="font-family: 'Inter', sans-serif; max-width: 600px; margin: 0 auto; padding: 30px;">
        <h2 style="color: #6C63FF;">Welcome to VoteSecure!</h2>
        <p>Hi {user.username},</p>
        <p>Thank you for registering. Please click the button below to verify your email address:</p>
        <p style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}" 
               style="background: linear-gradient(135deg, #6C63FF, #3B82F6); color: white; 
                      padding: 14px 32px; text-decoration: none; border-radius: 8px; 
                      font-weight: 600; display: inline-block;">
                Verify Email
            </a>
        </p>
        <p style="color: #888; font-size: 14px;">
            This link will expire in 24 hours. If you didn't create this account, 
            please ignore this email.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #aaa; font-size: 12px;">VoteSecure — Secure Online Voting Platform</p>
    </div>
    """
    send_mail(
        subject=subject,
        message=strip_tags(html_message),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )


def verify_email_view(request, token):
    """
    Verify a user's email address using the token from the verification link.
    Activates the user account and marks the profile as verified.
    """
    try:
        verification = EmailVerificationToken.objects.get(token=token)
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('login')

    if verification.is_expired:
        messages.error(request, 'This verification link has expired. Please register again.')
        # Clean up expired token and inactive user
        user = verification.user
        verification.delete()
        if not user.is_active:
            user.delete()
        return redirect('register')

    # Activate the user
    user = verification.user
    user.is_active = True
    user.save()

    # Mark profile as verified
    if hasattr(user, 'voter_profile'):
        user.voter_profile.is_verified = True
        user.voter_profile.save()

    # Clean up the token
    verification.delete()

    messages.success(request, 'Email verified successfully! You can now log in.')
    return redirect('login')


def login_view(request):
    """
    Handle voter login with styled form.
    Redirects to dashboard on success.
    """
    if request.user.is_authenticated:
        return redirect('voter_dashboard')

    if request.method == 'POST':
        form = VoterLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            # Redirect admins to admin dashboard
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('voter_dashboard')
    else:
        form = VoterLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Log out the user and redirect to login page."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    """
    View and update voter profile.
    """
    profile, created = VoterProfile.objects.get_or_create(
        user=request.user,
        defaults={'full_name': request.user.get_full_name() or request.user.username}
    )

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST)
        if form.is_valid():
            profile.full_name = form.cleaned_data['full_name']
            profile.phone = form.cleaned_data.get('phone', '')
            profile.address = form.cleaned_data.get('address', '')
            profile.date_of_birth = form.cleaned_data.get('date_of_birth')
            profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(initial={
            'full_name': profile.full_name,
            'phone': profile.phone,
            'address': profile.address,
            'date_of_birth': profile.date_of_birth,
        })

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile,
    })


def resend_verification_view(request):
    """Resend verification email for unverified accounts."""
    if request.method == 'POST':
        email = request.POST.get('email', '')
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(email=email, is_active=False)
            # Delete old token if exists
            EmailVerificationToken.objects.filter(user=user).delete()
            # Create new token
            token = EmailVerificationToken.objects.create(user=user)
            _send_verification_email(user, token)
            messages.success(request, 'Verification email resent. Please check your inbox.')
        except User.DoesNotExist:
            messages.error(request, 'No unverified account found with this email.')
    return redirect('login')
