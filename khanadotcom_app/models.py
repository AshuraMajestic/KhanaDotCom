from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator
from django.conf import settings
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username or None, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    USER_TYPES = (
        ("customer", "Customer"),
        ("delivery_person", "Delivery Person"),
        ("restaurant_owner", "Restaurant Owner"),
    )
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    access_token=models.TextField(blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.name

    class Meta:
        db_table = "user"
        managed = True


class FailedLoginAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    attempt_count = models.IntegerField(default=0)

    class Meta:
        db_table = "failed_login_attempt"
        managed = False


class CustomerDetail(models.Model):
    customer_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.name}'s Details"

    class Meta:
        db_table = "customer_details"
        managed = False


class RestaurantOwner(models.Model):
    restaurant_owner_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    aadhaar_card_number = models.CharField(
        max_length=12, unique=True, blank=False, null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.name

    class Meta:
        db_table = "restaurant_owner_detail"
        managed = False


class Restaurant(models.Model):
    restaurant_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(RestaurantOwner, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    profile_pic = models.ImageField(
        upload_to="restaurant_logo/", null=True, blank=True
    )
    description = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2,default=0.00, blank=True, null=True)
    restaurant_GST = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "restaurant_details"
        managed = False


class DeliveryPerson(models.Model):
    delivery_person_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicle_details = models.CharField(max_length=255, blank=True, null=True)
    availability_status = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    aadhaar_card_number = models.CharField(
        max_length=12, unique=True, blank=False, null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.name

    class Meta:
        db_table = "delivery_person_details"
        managed = False


class MenuItem(models.Model):
    menu_item_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    menu_item_pic = models.ImageField(upload_to="menu_items/", null=True, blank=True)
    availability = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2,default=0.00, blank=True, null=True)
    preparation_time = models.IntegerField(
        help_text="Preparation time in minutes", blank=True, null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "menu_item_details"
        managed = False


class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("preparing", "Preparing"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="pending"
    )
    delivery_address = models.TextField()

    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    delivery_person = models.ForeignKey(
        "DeliveryPerson", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} for {self.user.name}"

    def assign_delivery_person(self):
        available_delivery_person = DeliveryPerson.objects.filter(
            availability_status=True
        ).first()
        if available_delivery_person:
            self.delivery_person = available_delivery_person
            self.order_status = "out_for_delivery"
            available_delivery_person.availability_status = False
            available_delivery_person.save()
            self.save()
            return True
        else:
            return False

    class Meta:
        db_table = "order"
        managed = False


class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    availability = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.menu_item.name} (x{self.quantity})"

    class Meta:
        db_table = "order_item"
        managed = False


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ("credit_card", "Credit Card"),
        ("debit_card", "Debit Card"),
        ("net_banking", "Net Banking"),
        ("cash_on_delivery", "Cash on Delivery"),
        ("upi", "UPI"),
    )

    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default="pending")
    transaction_id = models.CharField(
        max_length=255, blank=True, null=True, unique=True
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.payment_id} for Order {self.order.order_id}"

    class Meta:
        db_table = "payment"
        managed = False


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, blank=True, null=True
    )
    customer = models.ForeignKey(
        CustomerDetail, on_delete=models.CASCADE, related_name="reviews"
    )
    delivery_person = models.ForeignKey(
        DeliveryPerson, on_delete=models.CASCADE, blank=True, null=True
    )
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.name}"

    class Meta:
        db_table = "review"
        managed = False


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "category"
        managed = False


class MenuItemCategory(models.Model):
    menu_item_category_id = models.AutoField(primary_key=True)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.menu_item.name} - {self.category.name}"

    class Meta:
        db_table = "menu_item_category"
        managed = False


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.name}"

    class Meta:
        db_table = "notification"
        managed = False


class Coupon(models.Model):
    coupon_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = "coupon"
        managed = False


# class SMSLogs(models.Model):
#     mobile_no_validator = RegexValidator(
#         regex=r"^\d{4,11}$",  # Example: 4 to 11 digits
#         message="Mobile number must be between 4 and 11 digits.",
#     )
#     uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     sended_by = models.CharField(
#         db_column="sended_by", default="noreply", max_length=50, blank=False, null=False
#     )
#     sended_to = models.CharField(
#         db_column="sended_to",
#         max_length=50,
#         validators=[mobile_no_validator],
#         blank=False,
#         null=False,
#     )
#     is_send = models.IntegerField(default=0)
#     is_read = models.BooleanField(default=False)
#     read_at = models.DateTimeField(blank=True, null=True)
#     message = models.TextField(blank=False, null=False)
#     sent_date = models.DateTimeField()
#     to_be_sent_date = models.DateTimeField(blank=True, null=True)
#     added_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="added_sms_log",
#         db_column="added_by",
#     )
#     application = models.ForeignKey(
#         "YourApp.Application",
#         on_delete=models.CASCADE,
#         default=None,  # Update default value as per your logic
#         related_name="application_sms_log",
#     )
#     candidate = models.ForeignKey(
#         "YourApp.CandidateDetails",
#         on_delete=models.CASCADE,
#         default=None,  # Update default value as per your logic
#     )
#     is_otp = models.IntegerField()
#     dlt_te_id = models.CharField(
#         db_column="dlt_te_id", max_length=100, blank=False, null=True
#     )
#     ip_address = models.CharField(
#         blank=False, null=False, max_length=150, default="0.0.0.0"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     is_deleted = models.BooleanField(default=False)
#     is_update = models.IntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = "sms_logs"


class EmailsLogs(models.Model):
    uid = models.CharField(max_length=200, default=uuid.uuid4, unique=True)
    sender = models.CharField(
        db_column="sender",
        default="KhanaDotCom",
        max_length=50,
        blank=False,
        null=False,
    )
    recipient = models.EmailField(
        db_column="recipient",
        max_length=50,
        blank=False,
        null=False,
        default="example@example.com",
    )
    is_sent = models.IntegerField(default=0)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=False, null=False)
    subject = models.CharField(max_length=500, null=True)
    attachment = models.CharField(max_length=500, blank=True, null=True)
    sent_cc = models.CharField(max_length=500, blank=True, null=True)
    sent_bcc = models.CharField(max_length=500, blank=True, null=True)
    sent_date = models.DateTimeField()
    to_be_sent_date = models.DateTimeField(blank=True, null=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="added_email_logs",
        db_column="added_by",
    )
    is_otp = models.IntegerField()
    ip_address = models.CharField(
        blank=False, null=False, max_length=150, default="0.0.0.0"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    sender_name = models.CharField(
        db_column="sender_name",
        default="Bablu",
        max_length=50,
        blank=False,
        null=False,
    )
    is_update = models.IntegerField(blank=True, null=True)
    is_smtp = models.BooleanField(default=False)

    class Meta:
        db_table = "email_log"
        managed = False


class ContactMessage(models.Model):
    message_id = models.CharField(max_length=200, default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "message_contact"
        managed = False
