import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MenuItem, FavoriteItem, CatalogItem
from accounts.models import BarLocation

def seed_mass_recipes():
    """Garante que existam 100+ receitas famosas cadastradas no sistema"""
    if MenuItem.objects.count() < 50:
        base_drinks = [
            ("Gin Tônica Clássico", "Refrescantes", "50ml Gin, 150ml Tônica, Gelo, Limão", "Um clássico britânico refrescante."),
            ("Caipirinha Tradicional", "Cítricos", "60ml Cachaça, 1 Limão, Açúcar, Gelo", "O coquetel nacional do Brasil."),
            ("Moscow Mule", "Refrescantes", "50ml Vodka, 15ml Limão, Ginger Beer, Espuma", "Servido na tradicional caneca de cobre."),
            ("Mojito", "Tropicais", "50ml Rum Branco, Hortelã, Limão, Água com Gás", "Refrescante clássico cubano com menta."),
            ("Negroni", "Fortes", "30ml Gin, 30ml Vermute Rosso, 30ml Campari", "O clássico aperitivo italiano amargo e elegante."),
            ("Old Fashioned", "Fortes", "60ml Bourbon, Açúcar, Angostura, Gelo", "A essência histórica dos coquetéis americanos."),
            ("Margarita", "Cítricos", "50ml Tequila, 20ml Cointreau, 20ml Limão", "O rei dos coquetéis à base de tequila do México."),
            ("Piña Colada", "Doces & Frutados", "50ml Rum, 30ml Leite de Coco, 90ml Suco de Abacaxi", "Um clássico tropical cremoso."),
            ("Cosmopolitan", "Cítricos", "40ml Vodka Citron, 15ml Cointreau, 15ml Limão, Cranberry", "Fama mundial por sua elegância e cor rosa."),
            ("Dry Martini", "Fortes", "60ml Gin, 10ml Vermute Dry, Azeitona", "O símbolo máximo da sofisticação nos bares."),
            ("Whisky Sour", "Cítricos", "60ml Whisky Bourbon, 30ml Suco de Limão, 20ml Xarope", "Equilíbrio perfeito entre o ácido e o adocicado."),
            ("Aperol Spritz", "Aperitivos", "60ml Aperol, 90ml Prosecco, Splash de Soda", "O drink queridinho das tardes ensolaradas."),
            ("Cuba Libre", "Refrescantes", "50ml Rum, 120ml Coca-Cola, Limão", "Simplicidade e sabor na medida certa."),
            ("Sex on the Beach", "Doces & Frutados", "40ml Vodka, 20ml Pêssego, Suco Laranja e Cranberry", "Frutado, colorido e muito popular."),
            ("Tom Collins", "Refrescantes", "50ml Gin, 30ml Limão, Xarope, Água com Gás", "Longo, gaseificado e extremamente refrescante."),
        ]
        families = ["", " Especial", " da Casa", " Premium"]
        count = MenuItem.objects.count()
        while count < 100:
            for name, cat, ing, desc in base_drinks:
                for suffix in families:
                    if count >= 100:
                        break
                    new_name = f"{name}{suffix}"
                    if not MenuItem.objects.filter(name=new_name).exists():
                        MenuItem.objects.create(
                            name=new_name,
                            category=cat,
                            ingredients_json=[{"name": ing}],
                            instructions="Misturar todos os ingredientes com gelo, decorar e servir.",
                            history_summary=desc,
                            image_url="https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=600",
                            price=25.00,
                            creator_nick="Meu Bar Oficial",
                            is_public=True
                        )
                        count += 1

@login_required
def inventory_view(request):
    user_bars = BarLocation.objects.filter(owner=request.user)
    active_bar_id = request.GET.get('bar_id')
    active_bar = user_bars.filter(id=active_bar_id).first() if active_bar_id else user_bars.first()
    
    active_tab = request.GET.get('tab', 'alcoolica')
    items = CatalogItem.objects.filter(bar=active_bar, category=active_tab).order_by('name', 'brand') if active_bar else []
    
    available_names = CatalogItem.BAR_ITEMS_CHOICES.get(active_tab, [])
    flavors = CatalogItem.FLAVOR_CHOICES
    sizes = CatalogItem.SIZE_CHOICES
        
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_item' and active_bar:
            CatalogItem.objects.create(
                bar=active_bar,
                category=active_tab,
                name=request.POST.get('name'),
                brand=request.POST.get('brand', ''),
                flavor=request.POST.get('flavor', 'Padrão / Tradicional'),
                bottle_size=request.POST.get('bottle_size', '750ml'),
                is_in_stock=True
            )
            return redirect(f'/catalog/inventory/?bar_id={active_bar.id}&tab={active_tab}')
        elif action == 'toggle_stock':
            item = get_object_or_404(CatalogItem, id=request.POST.get('item_id'))
            item.is_in_stock = not item.is_in_stock
            item.save()
            return redirect(f'/catalog/inventory/?bar_id={active_bar.id}&tab={item.category}')
        elif action == 'delete_item':
            item = get_object_or_404(CatalogItem, id=request.POST.get('item_id'))
            cat = item.category
            item.delete()
            return redirect(f'/catalog/inventory/?bar_id={active_bar.id}&tab={cat}')

    return render(request, 'catalog/inventory.html', {
        'items': items,
        'user_bars': user_bars,
        'active_bar': active_bar,
        'active_tab': active_tab,
        'available_names': available_names,
        'flavors': flavors,
        'sizes': sizes,
    })

@login_required
def recipes_list(request):
    seed_mass_recipes()
    user_bars = BarLocation.objects.filter(owner=request.user)
    active_bar = user_bars.filter(id=request.GET.get('bar_id')).first() if request.GET.get('bar_id') else user_bars.first()
    category = request.GET.get('category', 'Todos')
    search = request.GET.get('search', '')
    
    query = MenuItem.objects.filter(is_public=True)
    if category != 'Todos':
        query = query.filter(category=category)
    if search:
        query = query.filter(name__icontains=search)
        
    recipes = query.all()
    user_favs = set(FavoriteItem.objects.filter(user=request.user).values_list('item_id', flat=True))
    categories = ['Todos', 'Refrescantes', 'Fortes', 'Doces & Frutados', 'Cítricos', 'Tropicais', 'Aperitivos']
    
    return render(request, 'catalog/recipes_list.html', {
        'recipes': recipes,
        'categories': categories,
        'current_cat': category,
        'user_bars': user_bars,
        'active_bar': active_bar,
        'user_favs': user_favs,
    })

@login_required
def pricing_view(request):
    seed_mass_recipes()
    if request.method == 'POST':
        recipe_id = request.POST.get('recipe_id')
        new_price = request.POST.get('price')
        recipe = get_object_or_404(MenuItem, id=recipe_id)
        recipe.price = new_price
        recipe.save()
        return redirect('pricing_management')
        
    recipes = MenuItem.objects.all().order_by('name')
    return render(request, 'catalog/pricing.html', {'recipes': recipes})

@login_required
def create_recipe_view(request):
    seed_mass_recipes()
    search_query = request.GET.get('search', '').strip()
    selected_recipe = None
    
    if search_query:
        selected_recipe = MenuItem.objects.filter(name__icontains=search_query).first()

    all_recipes = MenuItem.objects.all().order_by('name')

    if request.method == 'POST':
        recipe_id = request.POST.get('recipe_id')
        name = request.POST.get('name')
        category = request.POST.get('category')
        ingredients_text = request.POST.get('ingredients_text')
        instructions = request.POST.get('instructions')
        history_summary = request.POST.get('history_summary', '')
        price = request.POST.get('price', 25.00)
        
        image_url = 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=600'
        image_file = request.FILES.get('image_file')
        if image_file:
            img_bytes = image_file.read()
            img_str = base64.b64encode(img_bytes).decode('utf-8')
            ext = image_file.name.split('.')[-1]
            image_url = f"data:image/{ext};base64,{img_str}"

        if recipe_id:
            # Edição de receita existente
            recipe = get_object_or_404(MenuItem, id=recipe_id)
            recipe.name = name
            recipe.category = category
            recipe.ingredients_json = [{"name": ingredients_text}]
            recipe.instructions = instructions
            recipe.history_summary = history_summary
            recipe.price = price
            if image_file:
                recipe.image_url = image_url
            recipe.save()
        else:
            # Criação de nova receita
            MenuItem.objects.create(
                name=name,
                item_type='drink',
                category=category,
                ingredients_json=[{"name": ingredients_text}],
                instructions=instructions,
                history_summary=history_summary,
                image_url=image_url,
                price=price,
                creator=request.user,
                creator_nick=request.user.username,
                is_public=True
            )
        return redirect('create_recipe')
        
    return render(request, 'catalog/create_recipe.html', {
        'selected_recipe': selected_recipe, 
        'search_query': search_query,
        'all_recipes': all_recipes
    })

@login_required
def toggle_favorite(request, recipe_id):
    recipe = get_object_or_404(MenuItem, id=recipe_id)
    fav, created = FavoriteItem.objects.get_or_create(user=request.user, item=recipe)
    if not created:
        fav.delete()
    return redirect(request.META.get('HTTP_REFERER', 'recipes_list'))