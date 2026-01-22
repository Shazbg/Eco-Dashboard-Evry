from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.vehicles.models import VehicleData, EmissionFactor


def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'core/login.html')


def logout_view(request):
    """Vue de déconnexion"""
    auth_logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Vue du tableau de bord"""
    context = {
        'vehicle_count': VehicleData.objects.filter(user=request.user).count(),
        'emission_factors_count': EmissionFactor.objects.filter(is_active=True).count(),
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def send_reminder_email(request):
    """
    Envoie un email de rappel à tous les agents pour saisir leurs données.
    Réservé aux administrateurs.
    """
    from django.contrib.auth.models import User
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.conf import settings
    from django.utils import timezone
    import logging
    
    # Vérifier que l'utilisateur est admin
    if not request.user.is_staff:
        messages.error(request, "⛔ Accès refusé. Cette fonctionnalité est réservée aux administrateurs.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Récupérer tous les users actifs (sauf admins et ceux sans email)
        recipients = User.objects.filter(
            is_active=True,
            is_staff=False
        ).exclude(email='')
        
        # Envoyer l'email
        sent_count = 0
        failed_count = 0
        
        for user in recipients:
            try:
                # Préparer le message
                message = render_to_string('emails/reminder.txt', {
                    'user': user,
                    'year': timezone.now().year,
                    'domain': request.get_host()
                })
                
                # Envoyer
                send_mail(
                    subject=f"Rappel - Saisie du bilan carbone {timezone.now().year}",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                sent_count += 1
                
            except Exception as e:
                failed_count += 1
                logging.error(f"Erreur envoi email à {user.email}: {e}")
        
        # Message de retour
        if sent_count > 0:
            messages.success(request, f"✅ {sent_count} email(s) envoyé(s) avec succès")
        if failed_count > 0:
            messages.warning(request, f"⚠️ {failed_count} email(s) n'ont pas pu être envoyé(s)")
        
        return redirect('dashboard')
    
    # GET : Afficher page de confirmation
    recipients_count = User.objects.filter(
        is_active=True,
        is_staff=False
    ).exclude(email='').count()
    
    return render(request, 'core/confirm_send_email.html', {
        'recipients_count': recipients_count,
        'current_year': timezone.now().year
    })
