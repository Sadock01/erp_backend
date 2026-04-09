from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductVariant, ProductImage


class ProductImageInline(admin.TabularInline):
    """Inline pour les images de produits"""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'sort_order']


class ProductVariantInline(admin.TabularInline):
    """Inline pour les variants de produits"""
    model = ProductVariant
    extra = 1
    fields = ['name', 'sku', 'variant_type', 'value', 'price_modifier', 'stock_quantity', 'is_active']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Configuration Django Admin pour les catégories"""
    list_display = ['name', 'parent', 'is_active', 'sort_order', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['sort_order', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'description', 'parent')
        }),
        ('Configuration', {
            'fields': ('image', 'is_active', 'sort_order')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Configuration Django Admin pour les produits"""
    list_display = [
        'name', 'sku', 'category', 'status', 'price', 
        'is_featured', 'total_stock_display', 'created_at'
    ]
    list_filter = [
        'status', 'product_type', 'category', 'is_digital', 
        'is_featured', 'created_at'
    ]
    search_fields = ['name', 'sku', 'barcode', 'description', 'tags']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at', 'total_stock_display']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'description', 'short_description', 'category')
        }),
        ('Codes et identification', {
            'fields': ('sku', 'barcode')
        }),
        ('Configuration', {
            'fields': ('product_type', 'status', 'is_digital', 'is_featured')
        }),
        ('Prix et coûts', {
            'fields': ('price', 'cost_price')
        }),
        ('Caractéristiques physiques', {
            'fields': ('weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('SEO et marketing', {
            'fields': ('tags', 'meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Stock et statistiques', {
            'fields': ('total_stock_display',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [ProductVariantInline, ProductImageInline]
    
    def total_stock_display(self, obj):
        """Affiche la quantité totale en stock"""
        total = obj.get_stock_quantity()
        if total > 0:
            return format_html('<span style="color: green;">{}</span>', total)
        else:
            return format_html('<span style="color: red;">{}</span>', total)
    total_stock_display.short_description = 'Stock total'
    total_stock_display.admin_order_field = 'variants__stock_quantity'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Configuration Django Admin pour les variants de produits"""
    list_display = [
        'name', 'product', 'sku', 'variant_type', 'value', 
        'final_price_display', 'stock_quantity', 'is_active'
    ]
    list_filter = ['variant_type', 'is_active', 'product__category']
    search_fields = ['name', 'sku', 'value', 'product__name']
    ordering = ['product', 'sort_order', 'name']
    readonly_fields = ['created_at', 'updated_at', 'final_price_display']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('product', 'name', 'sku', 'variant_type', 'value')
        }),
        ('Prix et stock', {
            'fields': ('price_modifier', 'final_price_display', 'stock_quantity')
        }),
        ('Configuration du stock', {
            'fields': ('min_stock_level', 'max_stock_level'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('is_active', 'sort_order')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def final_price_display(self, obj):
        """Affiche le prix final de la variante"""
        return f"{obj.final_price:.2f} €"
    final_price_display.short_description = 'Prix final'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Configuration Django Admin pour les images de produits"""
    list_display = ['product', 'image_preview', 'is_primary', 'sort_order', 'created_at']
    list_filter = ['is_primary', 'product__category']
    search_fields = ['product__name', 'alt_text']
    ordering = ['product', 'sort_order']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('product', 'image', 'image_preview', 'alt_text')
        }),
        ('Configuration', {
            'fields': ('is_primary', 'sort_order')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def image_preview(self, obj):
        """Affiche un aperçu de l'image"""
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return "Aucune image"
    image_preview.short_description = 'Aperçu'
