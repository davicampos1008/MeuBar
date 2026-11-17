import random
from django.db import models
from accounts.models import BarLocation
from bar_catalog.models import MenuItem

def generate_table_password():
    return f"{random.randint(1000, 9999)}"

class TableSession(models.Model):
    bar = models.ForeignKey(BarLocation, on_delete=models.CASCADE, related_name='sessions')
    table_number = models.CharField(max_length=20, default='Balcão')
    client_name = models.CharField(max_length=100)
    table_password = models.CharField(max_length=6, default=generate_table_password)
    is_active = models.BooleanField(default=True)
    is_fixed_bar = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        tipo = "Bar Fixo" if self.is_fixed_bar else f"Mesa {self.table_number}"
        return f"{tipo} - {self.client_name}"

class OrderItem(models.Model):
    session = models.ForeignKey(TableSession, on_delete=models.CASCADE, related_name='orders')
    recipe = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    observation = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, default='Pendente')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity}x {self.recipe.name}"