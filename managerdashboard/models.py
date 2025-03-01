from django.db import models
from authentication.models import User
from decimal import Decimal
import uuid
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone  # Use the correct timezone module

# Create your models here.
def generate_unique_id():
    return uuid.uuid4().hex

class Provider(models.Model):
    name = models.CharField(max_length=200)
    api_url = models.URLField()
    api_key = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProviderTransaction(models.Model):
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(
        max_length=10, choices=[("credit", "Credit"), ("debit", "Debit")]
    )
    notes = models.TextField(blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} - ${self.amount} - {self.provider.name}"


class ServiceCategory(models.Model):
    STATUS_CHOICES = [
        (0, "Inactive"),
        (1, "Active"),
    ]
    # Auto-generated fields
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID
    ids = models.CharField(
        max_length=32, default=generate_unique_id, editable=False, unique=True
    )  # Auto-generated UUID
    created = models.DateTimeField(auto_now_add=True)  # Auto-set on creation
    changed = models.DateTimeField(auto_now=True)  # Auto-updated on save
    sort = models.PositiveIntegerField(editable=False)  # Auto-generated sequence
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True, default="")
    image = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)

    class Meta:
        db_table = "categories"
        ordering = ["sort"]  # Changed from 'name' to use sort order
        verbose_name_plural = "Service Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate sort order as next available position
        if not self.sort:
            max_sort = (
                ServiceCategory.objects.aggregate(models.Max("sort"))["sort__max"] or 0
            )
            self.sort = max_sort + 1
        super().save(*args, **kwargs)


class Service(models.Model):
    ADD_TYPE_CHOICES = [("manual", "Manual"), ("api", "API")]

    STATUS_CHOICES = [
        (0, "Inactive"),
        (1, "Active"),
    ]

    # Auto-generated fields
    id = models.AutoField(primary_key=True)
    ids = models.CharField(
        max_length=32, default=generate_unique_id, editable=False, unique=True
    )
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    cate_id = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        db_column="cate_id",
        related_name="services",
    )
    api_provider_id = models.IntegerField(null=True, blank=True)

    # Service details
    name = models.CharField(max_length=255)
    desc = CKEditor5Field('Text', config_name='extends')
    price = models.DecimalField(max_digits=15, decimal_places=4)
    original_price = models.DecimalField(
        max_digits=15, decimal_places=4, null=True, blank=True
    )
    min = models.IntegerField()
    max = models.IntegerField()

    # Service configuration
    add_type = models.CharField(
        max_length=6, choices=ADD_TYPE_CHOICES, default="manual"
    )
    type = models.CharField(max_length=100, default="default")
    api_service_id = models.CharField(max_length=200, null=True, blank=True)
    dripfeed = models.BooleanField(default=False)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)

    class Meta:
        db_table = "services"
        ordering = ["cate_id", "name"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

    def save(self, *args, **kwargs):
        if not self.ids:
            self.ids = uuid.uuid4().hex
        super().save(*args, **kwargs)


class ServiceUpdate(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="updates"
    )
    old_rate = models.DecimalField(max_digits=10, decimal_places=4)
    new_rate = models.DecimalField(max_digits=10, decimal_places=4)
    old_min = models.IntegerField()
    new_min = models.IntegerField()
    old_max = models.IntegerField()
    new_max = models.IntegerField()
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Update for {self.service.name} at {self.created_at}"


class PaymentMethod(models.Model):
    TYPE_CHOICES = [("manual", "Manual"), ("automatic", "Automatic")]
    FEE_TYPE_CHOICES = [("percentage", "Percentage"), ("fixed", "Fixed Amount")]

    id = models.AutoField(primary_key=True)
    ids = models.CharField(
        max_length=32, default=generate_unique_id, editable=False, unique=True
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    desc = CKEditor5Field('Text', config_name='extends', blank=True, null=True)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    exchng_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES, blank=True, null=True)
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    client_id = models.CharField(max_length=255, blank=True, null=True)
    client_secret = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    test_mode = models.BooleanField(default=False)
    icon = models.ImageField(upload_to="payment_icons/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Payment Gateway"
        verbose_name_plural = "Payment Gateways"


class Transactions(models.Model):
    STATUS_CHOICES = [
        ("waiting", "Waiting"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    uid = models.ForeignKey(User, on_delete=models.CASCADE, to_field='uid', db_column='uid')
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="waiting")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-created"]
        db_table = "transactions"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        if not self.total_amount:
            self.total_amount = self.amount + self.fee
        super().save(*args, **kwargs)

    def generate_transaction_id(self):
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        random_string = str(uuid.uuid4()).split("-")[0]
        return f"TXN-{timestamp}-{random_string}"

    def __str__(self):
        return f"{self.transaction_id} - {self.uid} - ${self.amount}"
    
class Order(models.Model):
    TYPE_CHOICES = [
        ('direct', 'direct'),
        ('api', 'api'),
    ]
    
    SUB_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Paused', 'Paused'),
        ('Completed', 'Completed'),
        ('Expired', 'Expired'),
        ('Canceled', 'Canceled'),
    ]
    
    STATUS_CHOICES = [
        ('completed', 'completed'),
        ('processing', 'processing'),
        ('inprogress', 'inprogress'),
        ('pending', 'pending'),
        ('partial', 'partial'),
        ('refunded', 'refunded'),
        ('canceled', 'canceled'),
    ]

    id = models.AutoField(primary_key=True)
    ids = models.CharField(
        max_length=32, default=generate_unique_id, editable=False, unique=True
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='direct'
    )
    cate_id = models.ForeignKey(
        'ServiceCategory',
        on_delete=models.PROTECT,
        db_column='cate_id',
        related_name='orders',
        null=True,
        blank=True
    )
    service_id = models.ForeignKey(
        'Service',
        on_delete=models.SET_NULL,
        db_column='service_id',
        to_field='ids',
        null=True,
        blank=True
    )
    main_order_id = models.IntegerField(null=True, blank=True)
    service_type = models.CharField(
        max_length=50,
        default='default',
        blank=True,
        null=True
    )
    api_provider_id = models.IntegerField(null=True, blank=True)
    api_service_id = models.CharField(max_length=200, null=True, blank=True)
    api_order_id = models.IntegerField(default=0, null=True, blank=True)
    uid = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        to_field='uid',
        db_column='uid',
        null=True,
        blank=True
    )
    link = models.CharField(max_length=191, blank=True, null=True)
    quantity = models.IntegerField(null=True, blank=True)
    usernames = models.TextField(blank=True, null=True)
    username = models.TextField(blank=True, null=True)
    hashtags = models.TextField(blank=True, null=True)
    hashtag = models.TextField(blank=True, null=True)
    media = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    sub_posts = models.IntegerField(null=True, blank=True)
    sub_min = models.IntegerField(null=True, blank=True)
    sub_max = models.IntegerField(null=True, blank=True)
    sub_delay = models.IntegerField(null=True, blank=True)
    sub_expiry = models.TextField(blank=True, null=True)
    sub_response_orders = models.TextField(blank=True, null=True)
    sub_response_posts = models.TextField(blank=True, null=True)
    sub_status = models.CharField(
        max_length=10,
        choices=SUB_STATUS_CHOICES,
        null=True,
        blank=True
    )
    charge = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    start_counter = models.CharField(max_length=191, default='0')
    remains = models.CharField(max_length=191, default='0')
    is_drip_feed = models.BooleanField(default=False)
    runs = models.IntegerField(default=0)
    interval = models.IntegerField(default=0)
    dripfeed_quantity = models.CharField(max_length=191, default='0')
    note = models.TextField(blank=True, null=True)
    changed = models.DateTimeField(auto_now=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'orders'



