from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("signup/", views.signup_api, name="signup_api"),
    path("login/", views.login_api, name="login_api"),
    path("logout/", views.logout_api, name="logout_api"),
    path("change-password/", views.change_pass_api, name="change_password_api"),
    path("activate/<uidb64>/<str:token>/", views.activate_api, name="activate_api"),
    path("profile-user/", views.user_profile_api, name="user_profile_api"),
    path("profile-owner/", views.owner_profile_api, name="owner_profile_api"),
    path(
        "profile-delivery-person/",
        views.delivery_person_profile_api,
        name="delivery_person_profile_api",
    ),
    path(
        "update-profile-user/",
        views.update_user_profile_api,
        name="update_profile_user",
    ),
    path(
        "update-profile-owner/",
        views.update_owner_profile_api,
        name="update_profile_owner",
    ),
    path(
        "edit-user-picture/", views.update_profile_picture_api, name="edit_user_picture"
    ),
    path(
        "update-profile-delivery-person/",
        views.update_delivery_person_profile_api,
        name="update_profile_delivery_person",
    ),
    path("add-restaurant/", views.add_restaurant_api, name="add_restaurant"),
    path("add-menu-items/", views.add_menu_item_api, name="add_menu_item"),
    path("delete-user/<int:user_id>/", views.delete_user_api, name="delete_user_api"),
    path("api/restaurants/", views.restaurant_list_api, name="restaurant_list_api"),
    path(
        "api/restaurants/<int:restaurant_id>/",
        views.restaurant_detail_api,
        name="restaurant_detail_api",
    ),
    path(
        "api/restaurants/<int:restaurant_id>/menu/",
        views.menu_items_api_by_restaurant,
        name="menu_items_by_restaurant_api",
    ),
    path(
        "api/menu/",
        views.menu_items_api,
        name="menu_items_api",
    ),
    path(
        "restaurants/<int:restaurant_id>/order/",
        views.order_placement_api,
        name="order_placement_api",
    ),
    path(
        "order/<int:order_id>/",
        views.confirm_order,
        name="confirm_order",
    ),
    path(
        "order/status/<int:order_id>/",
        views.get_order_status_api,
        name="get_order_status_api",
    ),
    path(
        "order/<int:order_id>/prepare/",
        views.update_order_status_to_preparing,
        name="update_order_status_to_preparing",
    ),
    path(
        "assign_order/<int:order_id>/",
        views.assign_order_to_delivery_person,
        name="assign_order",
    ),
    path("order/history/", views.order_history_api, name="order_history_api"),
    # Password reset paths
    path("password-reset/", views.request_password_reset, name="password_reset"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path("contact/", views.contact_us, name="contact_us"),
    path(
        "restaurants/<int:restaurant_id>/rate/",
        views.rate_restaurant_api,
        name="rate_restaurant",
    ),
    path(
        "menu/<int:menu_item_id>/rate",
        views.rate_menu_item_api,
        name="rate_menu_item",
    ),
    path(
        "delivery-person/<int:delivery_person_id>/rate",
        views.rate_delivery_person_api,
        name="rate_delivery_person",
    ),
]
