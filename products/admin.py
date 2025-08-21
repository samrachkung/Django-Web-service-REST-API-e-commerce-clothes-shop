# products/admin.py
from django.contrib import admin
from .models import Category, Product, Size, Color, ProductVariant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size', 'color', 'stock_qty')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_price', 'is_on_sale', 'is_in_stock', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductVariantInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Images', {
            'fields': ('images',),
            'description': 'Add image URLs as a JSON list: ["url1", "url2", "url3"]'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('size_name',)
    search_fields = ('size_name',)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('color_name', 'hex_code')
    search_fields = ('color_name',)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'stock_qty', 'is_in_stock')
    list_filter = ('size', 'color', 'product__category')
    search_fields = ('product__name',)
    list_editable = ('stock_qty',)