import uuid
import time
import random
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.fields import ArrayField

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    cj_category_id = models.CharField(max_length=100, null=True, blank=True)
    is_protected = models.BooleanField(
        default=False,
        help_text="If True, CJ sync runs will skip updating this category's parent."
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])


class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_TYPES = [
        ('vendor', 'Vendor Submitted'),
        ('cj_dropship', 'CJ Dropshipping / AliExpress'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    sku = models.CharField(max_length=100, unique=True, editable=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField(blank=True, null=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.IntegerField(default=0)
    is_unindexable = models.BooleanField(
        default=False,
        help_text="Set to True if product image fetches repeatedly fail, excluding it from search indexes."
    )
    search_vector = SearchVectorField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"PROD-{int(time.time())}-{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class VendorProduct(models.Model):
    product = models.OneToOneField(
        Product,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='vendor_product'
    )
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='products')
    is_approved = models.BooleanField(default=False)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Flash sale price config
    flash_sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    flash_sale_start_at = models.DateTimeField(null=True, blank=True)
    flash_sale_end_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_flashsale_active(self):
        if self.flash_sale_price and self.flash_sale_start_at and self.flash_sale_end_at:
            return self.flash_sale_start_at <= timezone.now() <= self.flash_sale_end_at
        return False

    @property
    def effective_price(self):
        if self.is_flashsale_active:
            return self.flash_sale_price
        return self.product.price

    def __str__(self):
        return f"{self.product.name} (Vendor: {self.vendor.business_name})"


class DropshippingProduct(models.Model):
    product = models.OneToOneField(
        Product,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='dropshipping_product'
    )
    external_id = models.CharField(max_length=100, unique=True, help_text="CJ/AliExpress ID")
    cj_category_id = models.CharField(max_length=100, null=True, blank=True)
    price_markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    flat_markup_applied_eur = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cj_classifications = ArrayField(models.CharField(max_length=100), default=list, blank=True)
    is_superdeal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} (Dropshipped: {self.external_id})"


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True, help_text="Hot-linked asset URL")
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Set other images for the product to False
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    options = models.JSONField(default=dict, blank=True, help_text="e.g. {'Size': 'XL', 'Color': 'Blue'}")
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Added to base price")
    stock_quantity = models.IntegerField(default=0)

    def __str__(self):
        opt_str = ", ".join(f"{k}: {v}" for k, v in self.options.items())
        return f"{self.product.name} ({opt_str or 'No options'})"


class ProductAttribute(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=255, help_text="e.g., 'Weight', 'Material'")
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}: {self.value} ({self.product.name})"


class InventoryLog(models.Model):
    OP_TYPES = [
        ('purchase', 'Purchase'),
        ('restock', 'Restock'),
        ('refund', 'Refund'),
        ('manual_adjustment', 'Manual Adjustment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_logs')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_logs')
    operation_type = models.CharField(max_length=50, choices=OP_TYPES)
    quantity_change = models.IntegerField(help_text="Positive or negative quantity change")
    quantity_after = models.IntegerField(help_text="Quantity level after operation")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.operation_type} - {self.product.name} ({self.quantity_change})"


class ProductReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='product_reviews'
    )
    order_item = models.ForeignKey('orders.OrderItem', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    rating = models.IntegerField(help_text="Overall rating (1-5)")
    quality_rating = models.IntegerField(null=True, blank=True, help_text="1-5")
    value_rating = models.IntegerField(null=True, blank=True, help_text="1-5")
    accuracy_rating = models.IntegerField(null=True, blank=True, help_text="1-5")
    
    comment = models.TextField(blank=True, null=True)
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    reported_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.order_item and self.order_item.order.status == 'completed':
            self.is_verified_purchase = True
        
        super().save(*args, **kwargs)
        
        # Trigger recalculations of Vendor's denormalized ratings if vendor is associated
        try:
            from django.db.models import Avg
            if hasattr(self.product, 'vendor_product'):
                vendor = self.product.vendor_product.vendor
                if vendor:
                    reviews = ProductReview.objects.filter(product__vendor_product__vendor=vendor, is_approved=True)
                    stats = reviews.aggregate(avg=Avg('rating'), count=models.Count('id'))
                    vendor.rating_average = stats['avg'] or 0.00
                    vendor.rating_count = stats['count'] or 0
                    vendor.save(update_fields=['rating_average', 'rating_count'])
        except Exception:
            pass

    def __str__(self):
        return f"Review by {self.customer} for {self.product.name} (Rating: {self.rating})"


class ReviewHelpful(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        return f"{self.user} found review {self.review.id} helpful"


class ReviewReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Report by {self.user} on review {self.review.id}"
