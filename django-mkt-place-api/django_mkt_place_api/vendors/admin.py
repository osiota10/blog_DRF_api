from django.contrib import admin
from .models import Vendor, VendorPayout, VendorApplication, VendorReview, VendorAnalytics, VendorFollow, VendorFavourite, Banner, Promotion

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'verification_status', 'commission_rate', 'followers_count', 'rating_average')
    prepopulated_fields = {'business_slug': ('business_name',)}
    list_filter = ('verification_status', 'is_featured')
    search_fields = ('business_name', 'business_slug', 'user__email')

@admin.register(VendorPayout)
class VendorPayoutAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'amount', 'currency', 'status', 'period_start', 'period_end')
    list_filter = ('status', 'currency')
    search_fields = ('vendor__business_name',)

@admin.register(VendorApplication)
class VendorApplicationAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('business_name', 'user__email')

@admin.register(VendorReview)
class VendorReviewAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'customer', 'rating', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_verified_purchase')
    search_fields = ('vendor__business_name', 'customer__email')

@admin.register(VendorAnalytics)
class VendorAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'date', 'orders_count', 'revenue', 'store_views')
    list_filter = ('date',)
    search_fields = ('vendor__business_name',)

@admin.register(VendorFollow)
class VendorFollowAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'user', 'created_at')

@admin.register(VendorFavourite)
class VendorFavouriteAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'user', 'created_at')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'link_type', 'position', 'starts_at', 'ends_at')
    list_filter = ('link_type',)
    search_fields = ('title',)

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'promotion_type', 'starts_at', 'ends_at')
    list_filter = ('promotion_type',)
    search_fields = ('title',)
