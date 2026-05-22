from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

# 🌟 CORRECCIÓN DE IMPORTACIONES PARA AUTENTICACIÓN
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from .models import User, Product, Cart, CartItem, Category # Jalamos User desde aquí

# 🌟 FORMULARIO PERSONALIZADO DE REGISTRO
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",) # Agrega aquí más campos si tu modelo personalizado los pide (ej: 'email')

from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ProductForm

# ==========================================
# 🏠 SPRINT 5: HOME CON BÚSQUEDA, FILTRO Y PAGINACIÓN
# ==========================================
def home(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    # Optimización ORM
    products = Product.objects.select_related('owner').prefetch_related('categories').all()

    # Filtro de Búsqueda
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # Filtro de Categoría
    if category_id:
        products = products.filter(categories__id=category_id)

    # Paginación (6 productos por página)
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, 'store/home.html', {
        'page_obj': page_obj,
        'categories': categories
    })

# ==========================================
# 👤 AUTENTICACIÓN
# ==========================================
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Esto hace el login automático del paso 3
            return redirect('home') 
    else:
        form = CustomUserCreationForm()
    return render(request, 'store/register.html', {'form': form})
    
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# ==========================================
# 📊 GESTIÓN DE PRODUCTOS (VENDEDORES)
# ==========================================
@login_required
def dashboard(request):
    if not request.user.is_seller:
        return HttpResponseForbidden("No tienes permisos")
    products = Product.objects.filter(owner=request.user)
    return render(request, 'store/dashboard.html', {'products': products})

@login_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        product = form.save(commit=False)
        product.owner = request.user
        product.save()
        form.save_m2m()
        return redirect('dashboard')
    return render(request, 'store/product_form.html', {'form': form})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'store/product_form.html', {'form': form})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('dashboard')
    return render(request, 'store/product_confirm_delete.html', {'product': product})

    # ==========================================
# 🛒 SPRINT 4: CARRITO DE COMPRAS
# ==========================================
@login_required
def view_cart(request):
    # 🌟 CORRECCIÓN: Cambiamos user=request.user por cart_id=request.user.id
    cart, created = Cart.objects.get_or_create(cart_id=request.user.id)
    return render(request, 'store/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    # 1. Buscamos el producto por su ID
    product = get_object_or_404(Product, id=product_id)
    
    # 2. 🌟 CAMBIA ESTA LÍNEA (Usamos .id en lugar de .username)
    cart, created = Cart.objects.get_or_create(cart_id=request.user.id)
    
    # 3. Buscamos si el producto ya está en este carrito
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not item_created:
        # Si ya existía, sumamos 1 a la cantidad
        cart_item.quantity += 1
        cart_item.save()
        
    # 4. Redirigimos a la página del carrito
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    # Busca el artículo dentro del carrito y lo elimina
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('view_cart')