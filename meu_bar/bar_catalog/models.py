from django.db import models
from django.contrib.auth.models import User
from accounts.models import BarLocation

class CatalogItem(models.Model):
    CATEGORY_CHOICES = [
        ('alcoolica', 'Bebida Alcoólica'),
        ('mixer', 'Refrigerante, Suco & Mixer'),
        ('xarope', 'Xarope & Doce'),
        ('guarnicao', 'Guarnição & Erva'),
        ('copo', 'Copo & Vidraria'),
    ]
    
    BAR_ITEMS_CHOICES = {
        'alcoolica': ['Gin', 'Vodka', 'Rum', 'Cachaça', 'Whisky', 'Tequila', 'Vermute', 'Licor', 'Vinho', 'Espumante'],
        'mixer': ['Água Tônica', 'Schweppes Citrus', 'Água com Gás', 'Energético', 'Suco de Limão', 'Suco de Laranja', 'Ginger Beer'],
        'xarope': ['Xarope de Açúcar', 'Xarope de Frutas Vermelhas', 'Xarope de Maracujá', 'Grenadine', 'Mel'],
        'guarnicao': ['Hortelã', 'Limão Tahiti', 'Laranja', 'Alecrim', 'Pimenta Rosa', 'Gelo'],
        'copo': ['Taça Balloon', 'Copo Lowball', 'Copo Highball', 'Caneca de Cobre', 'Copo Shot']
    }

    FLAVOR_CHOICES = [
        ('Padrão / Tradicional', 'Padrão / Tradicional'),
        ('Tangerina / Citrus', 'Tangerina / Citrus'),
        ('Frutas Vermelhas', 'Frutas Vermelhas'),
        ('Maracujá', 'Maracujá'),
        ('Limão Siciliano', 'Limão Siciliano'),
        ('Baunilha', 'Baunilha'),
        ('Café / Espresso', 'Café / Espresso'),
        ('Canela / Especiarias', 'Canela / Especiarias'),
        ('Rosso', 'Rosso (Vermute)'),
        ('Bianco', 'Bianco (Vermute)'),
        ('Dry', 'Dry (Vermute/Gin)'),
        ('Cristal / Carta Branca', 'Cristal / Carta Branca'),
        ('Ouro / Reposado', 'Ouro / Reposado'),
    ]

    SIZE_CHOICES = [
        ('750ml', '750 ml'),
        ('1 Litro', '1 Litro (1000ml)'),
        ('1 Litro e Meio', '1,5 Litros'),
        ('350ml', '350 ml (Lata/Garrafa)'),
        ('269ml', '269 ml (Lata)'),
        ('Unidade', 'Por Unidade'),
        ('Porção', 'Porção a gosto'),
    ]
    
    bar = models.ForeignKey(BarLocation, on_delete=models.CASCADE, related_name='catalog_items')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True, null=True)
    flavor = models.CharField(max_length=100, default='Padrão / Tradicional', choices=FLAVOR_CHOICES)
    bottle_size = models.CharField(max_length=50, default='750ml', choices=SIZE_CHOICES)
    is_in_stock = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        flavor_txt = f" ({self.flavor})" if self.flavor != 'Padrão / Tradicional' else ""
        return f"{self.name} - {self.brand or 'Genérico'}{flavor_txt}"

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=20, default='drink')
    category = models.CharField(max_length=50, default='Refrescantes')
    ingredients_json = models.JSONField(default=list)
    instructions = models.TextField()
    history_summary = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=25.00) # Preço de venda
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    creator_nick = models.CharField(max_length=50, default='Meu Bar')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class FavoriteItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)