from django.contrib import admin
from .models import Category, Brand, Product, VendorProduct, DropshippingProduct, ProductImage, ProductVariant, ProductAttribute, InventoryLog, ProductReview, ReviewHelpful, ReviewReport

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'cj_category_id', 'is_protected')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_protected',)
    search_fields = ('name', 'cj_category_id')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'sku', 'price', 'stock_quantity', 'is_unindexable')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('product_type', 'is_unindexable', 'brand', 'category')
    search_fields = ('name', 'sku')
    inlines = [ProductImageInline, ProductVariantInline, ProductAttributeInline]

@admin.register(VendorProduct)
class VendorProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'vendor', 'is_approved', 'flash_sale_price', 'is_flashsale_active')
    list_filter = ('is_approved',)
    search_fields = ('product__name', 'vendor__business_name')

@admin.register(DropshippingProduct)
class DropshippingProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'external_id', 'cj_category_id', 'price_markup_percentage', 'is_superdeal')
    list_filter = ('is_superdeal',)
    search_fields = ('product__name', 'external_id')

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'price_adjustment', 'stock_quantity')

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'variant', 'operation_type', 'quantity_change', 'quantity_after', 'created_at')
    list_filter = ('operation_type', 'created_at')

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'rating', 'is_verified_purchase', 'is_approved', 'helpful_count')
    list_filter = ('rating', 'is_verified_purchase', 'is_approved')
    search_fields = ('product__name', 'customer__email', 'comment')
