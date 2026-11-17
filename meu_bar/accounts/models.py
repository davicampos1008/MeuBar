from django.db import models
from django.contrib.auth.models import User

class BarLocation(models.Model):
    BAR_TYPES = [
        ('home', 'Residencial (Casa - Sem preços/comanda)'),
        ('commercial_counter', 'Comercial - Retirada no Balcão'),
        ('commercial_tables', 'Comercial - Atendimento em Mesas'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bars')
    name = models.CharField(max_length=100)  # Ex: "Meu Bar de Casa", "Meu Bar Pub"
    bar_type = models.CharField(max_length=25, choices=BAR_TYPES, default='home')
    total_tables = models.PositiveIntegerField(default=0, help_text="Quantidade de mesas (se comercial)")
    created_at = models.DateTimeField(auto_now_add=True)

    def is_commercial(self):
        return self.bar_type in ['commercial_counter', 'commercial_tables']

    def __str__(self):
        return f"{self.name} ({self.get_bar_type_display()})"