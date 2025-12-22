from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification


@login_required
def afficher_notifications(request):
    notifications = Notification.objects.filter(utilisateur=request.user).order_by('-date_creation')
    return render(request, 'afficher_notifications.html', {'notifications': notifications})


@login_required
def marquer_notification_lu(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, utilisateur=request.user)
    notification.lu = True
    notification.save()
    messages.success(request, "Notification marquée comme lue.")
    return redirect('afficher_notifications')
