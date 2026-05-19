from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ProductForm
from .models import Product, Cart, CartItem, Category

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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
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