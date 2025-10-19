from django.contrib import admin
from .models import Category, Product, ProductImage, Cart, WishList,Review,Order
admin.site.register(Review)
admin.site.register(Order)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('alt_text', 'created_at', 'updated_at')
    search_fields = ('alt_text',)
    list_filter = ('created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('category', 'created_at', 'updated_at')
    filter_horizontal = ('images',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'is_active', 'total_price', 'created_at', 'updated_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('is_active', 'created_at', 'updated_at')

@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'is_notified', 'created_at', 'updated_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('is_notified', 'created_at', 'updated_at')
