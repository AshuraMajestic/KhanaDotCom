from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication related paths
    path("", views.SignupPage, name="signup"),
    path("login/", views.LoginPage, name="login"),
    path("home/", views.HomePage, name="home"),
    path("logout/", views.LogoutPage, name="logout"),
    # Password reset paths
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # Account activation path
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
    # Restaurant related paths
    path("restaurants/", views.restaurant_list_view, name="restaurant_list"),
    path(
        "restaurant/<int:restaurant_id>/",
        views.restaurant_detail_view,
        name="restaurant_detail",
    ),
    path(
        "restaurant/<int:restaurant_id>/menu/", views.menu_items_view, name="menu_item"
    ),
    # Order related paths
    path(
        "order/<int:restaurant_id>/", views.order_placement_view, name="order_placement"
    ),
    path(
        "order/confirmation/<int:order_id>/",
        views.order_confirmation_view,
        name="order_confirmation",
    ),
    # User profile and order history paths
    path("profile/", views.user_profile_view, name="user_profile"),
    path("order/history/", views.order_history_view, name="order_history"),
]
