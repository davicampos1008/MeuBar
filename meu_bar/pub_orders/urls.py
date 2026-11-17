from django.urls import path
from . import views

urlpatterns = [
    path('generator/', views.qr_generator_view, name='qr_generator'),
    path('client-menu/<int:bar_id>/', views.client_menu_view, name='client_menu'),
    path('live/', views.live_orders_view, name='live_orders'),
    path('sessions/', views.manage_sessions_view, name='manage_sessions'),
]