from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('catalog/', include('bar_catalog.urls')),
    path('orders/', include('pub_orders.urls')),  # <-- Esta linha estava faltando no arquivo principal!
    path('', lambda request: redirect('recipes_list'), name='home'),
]