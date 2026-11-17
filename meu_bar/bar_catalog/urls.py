from django.urls import path
from . import views

urlpatterns = [
    path('recipes/', views.recipes_list, name='recipes_list'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('pricing/', views.pricing_view, name='pricing_management'),
    path('create/', views.create_recipe_view, name='create_recipe'),
    path('favorite/<int:recipe_id>/', views.toggle_favorite, name='toggle_favorite'),
]