from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory, Payment, Coupon, Wishlist, ReturnRequest

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'is_active', 'total_items', 'subtotal', 'created_at')
    list_filter = ('is_active',)
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'payment_status', 'total', 'created_at')
    list_filter = ('status', 'payment_status')
    search_fields = ('order_number', 'customer__email')
    inlines = [OrderItemInline, OrderStatusHistoryInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'order', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency')
    search_fields = ('reference', 'order__order_number')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'usage_limit', 'usage_count', 'valid_until')
    list_filter = ('discount_type',)
    search_fields = ('code',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'customer', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason')
    search_fields = ('order__order_number', 'customer__email')
