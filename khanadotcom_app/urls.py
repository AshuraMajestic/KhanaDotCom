from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("signup/", views.signup_api, name="signup_api"),
    path("login/", views.login_api, name="login_api"),
    path("logout/", views.logout_api, name="logout_api"),
    path("token/", views.generate_token, name="generate_token"),
    path("activate/<uidb64>/<str:token>/", views.activate_api, name="activate_api"),
    path("profile/", views.user_profile_api, name="user_profile_api"),
    path("update-profile/", views.update_profile, name="update_profile"),
    path("delete-user/<int:user_id>/", views.delete_user_api, name="delete_user_api"),
    path("restaurants/", views.restaurant_list_api, name="restaurant_list_api"),
    path(
        "restaurants/<int:restaurant_id>/",
        views.restaurant_detail_api,
        name="restaurant_detail_api",
    ),
    path(
        "restaurants/<int:restaurant_id>/menu/",
        views.menu_items_api,
        name="menu_items_api",
    ),
    path(
        "restaurants/<int:restaurant_id>/order/",
        views.order_placement_api,
        name="order_placement_api",
    ),
    path(
        "order/<str:order_id>/",
        views.confirm_order,
        name="confirm_order",
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
]
