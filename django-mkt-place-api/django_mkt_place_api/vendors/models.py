import uuid
from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

class Vendor(models.Model):
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_profile'
    )
    business_name = models.CharField(max_length=255)
    business_slug = models.SlugField(max_length=255, unique=True)
    business_email = models.EmailField()
    business_phone = PhoneNumberField()
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Default platform commission fee rate")
    
    # Bank transfer coordinates
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    routing_number = models.CharField(max_length=50, null=True, blank=True)
    
    # Denormalized ratings and followers metrics
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rating_count = models.IntegerField(default=0)
    followers_count = models.IntegerField(default=0)
    
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name


class VendorPayout(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount to be paid out")
    currency = models.CharField(max_length=10, default='EUR')
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    order_count = models.IntegerField(default=0)
    
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Calculated net earnings (gross - commission)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.net_amount = self.gross_amount - self.commission_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payout - {self.vendor.business_name} - {self.net_amount} {self.currency}"


class VendorApplication(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_applications'
    )
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=100)
    business_email = models.EmailField()
    business_phone = PhoneNumberField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=2, help_text="ISO alpha-2 country code")
    description = models.TextField()
    products_description = models.TextField()
    expected_monthly_sales = models.CharField(max_length=50)
    
    business_certificate = models.FileField(upload_to='documents/', null=True, blank=True)
    identity_document = models.FileField(upload_to='documents/', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Application by {self.business_name} (Status: {self.status})"


class VendorReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_reviews'
    )
    rating = models.IntegerField(help_text="Overall rating (1-5)")
    product_quality_rating = models.IntegerField(null=True, blank=True, help_text="1-5")
    shipping_speed_rating = models.IntegerField(null=True, blank=True, help_text="1-5")
    customer_service_rating = models.IntegerField(null=True, blank=True, help_text="1-5")
    
    comment = models.TextField(blank=True, null=True)
    is_verified_purchase = models.BooleanField(default=False)
    vendor_response = models.TextField(blank=True, null=True)
    vendor_responded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer} for {self.vendor.business_name} (Rating: {self.rating})"


class VendorAnalytics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    
    # Sales metrics
    orders_count = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    items_sold = models.IntegerField(default=0)
    
    # Traffic metrics
    store_views = models.IntegerField(default=0)
    product_views = models.IntegerField(default=0)
    
    # Customer metrics
    new_customers = models.IntegerField(default=0)
    returning_customers = models.IntegerField(default=0)
    
    # Key Performance Indicators
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        verbose_name_plural = "Vendor Analytics"
        unique_together = ('vendor', 'date')

    def __str__(self):
        return f"Analytics - {self.vendor.business_name} on {self.date}"


class VendorFollow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='follows')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_follows'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vendor', 'user')

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            self.vendor.followers_count = VendorFollow.objects.filter(vendor=self.vendor).count()
            self.vendor.save(update_fields=['followers_count'])

    def delete(self, *args, **kwargs):
        vendor = self.vendor
        super().delete(*args, **kwargs)
        vendor.followers_count = VendorFollow.objects.filter(vendor=vendor).count()
        vendor.save(update_fields=['followers_count'])

    def __str__(self):
        return f"{self.user} follows {self.vendor.business_name}"


class VendorFavourite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='favourites')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_favourites'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vendor', 'user')

    def __str__(self):
        return f"{self.user} favourited {self.vendor.business_name}"


class Banner(models.Model):
    LINK_TYPES = [
        ('product', 'Product Link'),
        ('category', 'Category Link'),
        ('vendor', 'Vendor Link'),
        ('external', 'External URL'),
        ('none', 'No Redirection'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='banners/')
    link_type = models.CharField(max_length=20, choices=LINK_TYPES, default='none')
    link_target = models.CharField(max_length=255, null=True, blank=True, help_text="Slug, ID, or external URL depending on type")
    position = models.IntegerField(default=0, help_text="Display order sequence")
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Promotion(models.Model):
    PROMO_TYPES = [
        ('flash_sale', 'Flash Sale'),
        ('seasonal', 'Seasonal Campaign'),
        ('clearance', 'Clearance'),
        ('featured_vendor', 'Featured Vendor Promotion'),
        ('new_arrivals', 'New Arrivals Grouping'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    promotion_type = models.CharField(max_length=30, choices=PROMO_TYPES)
    
    products = models.ManyToManyField('products.Product', blank=True)
    categories = models.ManyToManyField('products.Category', blank=True)
    vendors = models.ManyToManyField(Vendor, blank=True)
    
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
