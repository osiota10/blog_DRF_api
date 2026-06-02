import uuid
import random
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.quantity * item.price for item in self.items.all())

    def __str__(self):
        if self.user:
            return f"Cart - {self.user.email}"
        return f"Guest Cart - {self.session_key}"


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Snapshot of price when added")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_actual_cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="Actual shipping cost paid to CJ")
    
    # CJ integrations
    cj_order_id = models.CharField(max_length=100, null=True, blank=True)
    cj_fulfillment_status = models.CharField(max_length=100, null=True, blank=True)
    cj_logistics_name = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def can_cancel(self):
        return self.status in ['pending', 'processing']

    def save(self, *args, **kwargs):
        if not self.order_number:
            date_str = timezone.now().strftime('%Y%m%d')
            rand_str = ''.join(random.choices('0123456789', k=4))
            self.order_number = f"ORD-{date_str}-{rand_str}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='order_items')
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=255)
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    variant_name = models.CharField(max_length=255, null=True, blank=True)
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in {self.order.order_number}"


class OrderStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    changed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Order Status Histories"

    def __str__(self):
        return f"Order {self.order.order_number} status change to {self.new_status}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='EUR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=100, unique=True, editable=False)
    
    # Stripe integration attributes
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True)
    
    gateway_response = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            rand_hex = ''.join(random.choices('0123456789ABCDEF', k=16))
            self.reference = f"PAY-{rand_hex}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reference


class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('flat', 'Flat Discount'),
        ('percentage', 'Percentage Discount'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    applicable_products = models.ManyToManyField('products.Product', blank=True)
    applicable_categories = models.ManyToManyField('products.Category', blank=True)

    def __str__(self):
        return self.code


class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} - {self.product.name}"


class ReturnRequest(models.Model):
    REASON_CHOICES = [
        ('damaged', 'Damaged Item'),
        ('wrong_item', 'Wrong Item Received'),
        ('not_as_described', 'Not As Described'),
        ('changed_mind', 'Changed Mind'),
        ('other', 'Other Reason'),
    ]

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('refunded', 'Refunded'),
        ('exchanged', 'Exchanged'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='return_requests')
    order_item = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='return_requests')
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='return_requests'
    )
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    images = models.JSONField(default=list, blank=True, help_text="List of evidence photo URLs")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return Request for {self.order.order_number}"
