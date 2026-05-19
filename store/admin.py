from django.contrib import admin
from .models import User, Category, Product, Cart, CartItem, Order, OrderItem

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_seller')
    list_filter = ('is_seller',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'owner')
    list_filter = ('categories',)
    search_fields = ('name',)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added') 
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')


# ==========================================
# 📦 NUEVO: Panel de Administración de Órdenes
# ==========================================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # No queremos filas vacías por defecto, solo ver lo que se compró
    readonly_fields = ('product', 'quantity', 'price') # Que no se pueda alterar el historial

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    inlines = [OrderItemInline]