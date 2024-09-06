from django.contrib import admin
from .models import (
    Restaurant,
    Order,
    MenuItem,
    OrderItem,
    FailedLoginAttempt,
    User,
    RestaurantOwner,
    DeliveryPerson,
    CustomerDetail,
    Review,
    Payment,
    Coupon,
    Category,
    MenuItemCategory,
    Notification,
    EmailsLogs,
    ContactMessage,
    Rating,
)

# Register your models here


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "user_type", "is_staff", "is_active")
    list_filter = ("user_type", "is_staff", "is_active")
    search_fields = ("name", "email")


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "address", "phone_number", "email")
    search_fields = ("name", "owner__name", "email")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "user", "total_amount", "order_status", "order_date")
    list_filter = ("order_status", "created_at")
    search_fields = ("user__name", "order_id")

    class OrderItemInline(admin.TabularInline):
        model = OrderItem

    inlines = [OrderItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "price", "availability")
    list_filter = ("restaurant", "availability")
    search_fields = ("name", "restaurant__name")

    class OrderItemInline(admin.TabularInline):
        model = OrderItem

    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "menu_item", "quantity", "price")
    list_filter = ("order__order_status", "menu_item__restaurant")
    search_fields = ("order__order_id", "menu_item__name")


@admin.register(FailedLoginAttempt)
class FailedLoginAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "timestamp")
    search_fields = ("user__email", "timestamp")
    list_filter = ("timestamp",)


admin.site.register(RestaurantOwner)
admin.site.register(DeliveryPerson)
admin.site.register(CustomerDetail)
admin.site.register(Review)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Category)
admin.site.register(MenuItemCategory)
admin.site.register(Notification)
admin.site.register(EmailsLogs)
admin.site.register(ContactMessage)
admin.site.register(Rating)
