#Les routes de l'application notification
from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.afficher_notifications, name='afficher_notifications'),
    path('notification/<int:notification_id>/marquer-lu/', views.marquer_notification_lu, name='marquer_notification_lu'),
]