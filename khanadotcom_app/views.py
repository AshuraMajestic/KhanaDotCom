from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.db import transaction
from .tokens import account_activation_token
from stdnum.in_ import aadhaar
import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.db.models.query_utils import Q
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .serializers import (
    OrderSerializer,
)
import re
from .models import (
    RestaurantOwner,
    DeliveryPerson,
    Order,
    Payment,
    OrderItem,
    MenuItem,
    Restaurant,
    CustomerDetail,
    FailedLoginAttempt,
)


User = get_user_model()


#  Authentication starts


def validate_password(password):
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")

    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")

    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit.")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character.")

    return True


def loginView(request):
    return render(request, "login.html")


def home(request):
    return render(request, "home.html")


def success(request):
    return render(request, "success.html")


@csrf_exempt
@api_view(["POST"])
def signup_api(request):
    if request.method == "POST":
        try:
            data = request.data
            username = data.get("username")
            name = data.get("name")
            email = data.get("email")
            password = data.get("password")
            user_type = data.get("user_type")
            phone_number = data.get("phone_number")
            address = data.get("address")
            aadhaar_number = data.get("aadhaar_number", "").replace(" ", "")
            vehicle_details = data.get("vehicle_details")
            date_of_birth = data.get("date_of_birth")

            if not (username and email and password and user_type):
                return JsonResponse(
                    {
                        "error": "All fields (username, email, password, user_type) are required."
                    },
                    status=400,
                )
            # Validate the password
            try:
                validate_password(password)
            except ValueError as e:
                return JsonResponse({"error": str(e)}, status=400)

            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    name=name,
                    user_type=user_type,
                    address=address,
                    phone_number=phone_number,
                )
                user.is_active = False

                # Validate Aadhaar number if required
                if (
                    user_type in ["restaurant_owner", "delivery_person"]
                    and not aadhaar_number
                ):
                    raise ValueError("Aadhaar number is required for this user type.")

                if aadhaar_number and not aadhaar.is_valid(aadhaar_number):
                    raise ValueError("Invalid Aadhaar number.")

                # Create profile based on user type
                if user_type == "restaurant_owner":
                    RestaurantOwner.objects.create(
                        user=user, aadhaar_card_number=aadhaar_number
                    )
                elif user_type == "delivery_person":
                    DeliveryPerson.objects.create(
                        user=user,
                        vehicle_details=vehicle_details,
                        aadhaar_card_number=aadhaar_number,
                    )
                else:
                    CustomerDetail.objects.create(
                        user=user, date_of_birth=date_of_birth
                    )

                # Save user only if profile creation is successful
                user.save()

            # Send activation email
            send_activation_email(request, user)

            return JsonResponse(
                {"success": "User created successfully. Check email for activation."},
                status=201,
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return JsonResponse(
                {"error": "Network Error" + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)


@csrf_exempt
@api_view(["POST"])
def login_api(request):
    if request.method == "POST":
        username = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            # Reset failed login attempts on successful login
            FailedLoginAttempt.objects.filter(user=user).delete()
            login(request, user)
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            token_data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return Response({"success": "Login successful.", "token": token_data})
        else:
            # Handle failed login attempts
            user = User.objects.filter(email=username).first()
            if user:
                failed_attempt, created = FailedLoginAttempt.objects.get_or_create(
                    user=user
                )
                failed_attempt.attempt_count += 1
                failed_attempt.timestamp = timezone.now()
                failed_attempt.save()

                if failed_attempt.attempt_count >= 5:
                    send_password_reset_email(request, user)
                    return Response(
                        {
                            "error": "Too many failed login attempts. Password reset email has been sent."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    else:
        return Response(
            {"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


@api_view(["POST"])
def logout_api(request):
    try:
        logout(request)
        return Response({"success": "Logout successful."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Network Error"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def activate_api(request, uidb64, token):
    try:
        uid = str(urlsafe_base64_decode(uidb64), encoding="utf-8")
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return Response({"success": "Account activated successfully."})
    else:
        return Response(
            {"error": "Activation link is invalid or expired."},
            status=status.HTTP_400_BAD_REQUEST,
        )


def send_activation_email(request, user):
    mail_subject = "Activate your account."
    message = render_to_string(
        "activate_account.html",
        {
            "user": user,
            "domain": get_current_site(request).domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        },
    )
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()


# authentication ends

@permission_classes([IsAuthenticated])
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def user_profile_api(request):
    user = request.user
    data = {
        "username": user.username,
        "email": user.email,
        "user_type": user.user_type,
    }
    return Response(data)


@api_view(["GET"])
def restaurant_list_api(request):
    restaurants = Restaurant.objects.all()
    data = [
        {"id": restaurant.restaurant_id, "name": restaurant.name}
        for restaurant in restaurants
    ]
    return Response(data)


@api_view(["GET"])
def restaurant_detail_api(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    data = {
        "id": restaurant.restaurant_id,
        "name": restaurant.name,
        "description": restaurant.description,
    }
    return Response(data)


@api_view(["GET"])
def menu_items_api(request, restaurant_id):
    menu_items = MenuItem.objects.filter(restaurant_id=restaurant_id)
    data = [
        {
            "id": item.menu_item_id,
            "name": item.name,
            "price": item.price,
            "description": item.description,
        }
        for item in menu_items
    ]
    return Response(data)


# Order placement api Starts


@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def order_placement_api(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)

    if request.method == "POST":
        data = request.data

        # Extract data from request body
        delivery_address = data.get("delivery_address")
        items = data.get("items", [])

        # Validate data presence
        if not (delivery_address and items):
            return Response(
                {"error": "Delivery address and items are required fields."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create Order object
        order = Order.objects.create(
            user=request.user,  # Assuming user is authenticated
            delivery_address=delivery_address,
            total_amount=0,  # Placeholder for total amount
        )

        # Process each selected menu item
        total_amount = 0

        for item_id in items:
            menu_item = get_object_or_404(MenuItem, pk=item_id)
            quantity = 1  # For simplicity, assuming quantity is always 1
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                price=menu_item.price,
            )
            total_amount += menu_item.price

        # Update total_amount in the Order model
        order.total_amount = total_amount
        order.save()

        # Create Payment object (example: cash on delivery)
        payment = Payment.objects.create(
            order=order,
            payment_method="cash_on_delivery",
            amount=total_amount,
            payment_status="pending",  # Adjust based on actual payment flow
        )

        # Return JSON response with order confirmation details
        return Response(
            {
                "success": "Order placed successfully.",
                "order_id": order.order_id,
                "total_amount": order.total_amount,
            },
            status=status.HTTP_201_CREATED,
        )

    else:
        # Return method not allowed error for non-POST requests
        return Response(
            {"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


@api_view(["GET"])
def order_confirmation_api(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    # Prepare data to return in the response
    order_data = {
        "order_id": order.order_id,
        "total_amount": order.total_amount,
        "order_date": order.order_date.strftime("%Y-%m-%d %H:%M:%S"),
    }

    return Response(order_data)


# Order placement api Ends


@api_view(["GET"])
def order_history_api(request):
    # Fetch orders for the current user (assuming user is authenticated)
    orders = Order.objects.filter(user=request.user).order_by("-order_date")

    # Serialize queryset into JSON data
    serializer = OrderSerializer(orders, many=True)

    return Response(serializer.data)


# # reset password api start


@api_view(["POST"])
def request_password_reset(request):
    data = request.data
    email = data.get("email")

    if not email:
        return Response(
            {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    users = User.objects.filter(Q(email=email))
    if not users.exists():
        return Response(
            {"error": "No user found with this email."},
            status=status.HTTP_404_NOT_FOUND,
        )

    for user in users:
        send_password_reset_email(request, user)

    return Response(
        {"success": "Password reset email has been sent."}, status=status.HTTP_200_OK
    )


def send_password_reset_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    mail_subject = "Password Reset Request"
    message = render_to_string(
        "password_reset_email.html",
        {
            "user": user,
            "domain": get_current_site(request).domain,
            "uid": uid,
            "token": token,
        },
    )
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()


@api_view(["GET", "POST"])
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if request.method == "GET":
        if user is not None and default_token_generator.check_token(user, token):
            # Render the password reset form
            return render(
                request,
                "password_reset_confirm.html",
                {"uidb64": uidb64, "token": token},
            )
        else:
            # Invalid token or user not found
            return Response(
                {"error": "Inavalid token or Expired Token"},
                status=status.HTTP_404_NOT_FOUND,
            )

    elif request.method == "POST":
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.data.get("new_password")

            if new_password:
                try:
                    validate_password(new_password)
                except ValueError as e:
                    return JsonResponse({"error": str(e)}, status=400)

                user.set_password(new_password)
                user.save()
                return JsonResponse(
                    {"message": "Password reset successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "invalid Token"}, status=status.HTTP_400_BAD_REQUEST
                )


# reset password api ends


# Update Api Starts


@api_view(["POST"])
def update_profile(request):
    user = request.user  # Get the logged-in user instance

    if request.method == "POST":
        try:
            data = request.data  # Use request.data to handle JSON payload

            # Update user fields if provided and not empty
            if "name" in data and data["name"].strip():
                user.name = data["name"].strip()
            if "phone_number" in data and data["phone_number"].strip():
                user.phone_number = data["phone_number"].strip()
            if "address" in data and data["address"].strip():
                user.address = data["address"].strip()
            if "profile_picture" in request.FILES:
                user.profile_picture = request.FILES["profile_picture"]

            # Save the updated user object
            user.save()

            # Check user type and update related model if applicable
            if user.user_type == "customer":
                customer_detail, created = CustomerDetail.objects.get_or_create(
                    user=user
                )
                if "date_of_birth" in data and data["date_of_birth"].strip():
                    customer_detail.date_of_birth = data["date_of_birth"].strip()
                customer_detail.save()
            elif user.user_type == "restaurant_owner":
                restaurant_owner, created = RestaurantOwner.objects.get_or_create(
                    user=user
                )
                if (
                    "aadhaar_card_number" in data
                    and data["aadhaar_card_number"].strip()
                ):
                    restaurant_owner.aadhaar_card_number = data[
                        "aadhaar_card_number"
                    ].strip()
                restaurant_owner.save()
            elif user.user_type == "delivery_person":
                delivery_person, created = DeliveryPerson.objects.get_or_create(
                    user=user
                )
                if "vehicle_details" in data and data["vehicle_details"].strip():
                    delivery_person.vehicle_details = data["vehicle_details"].strip()
                delivery_person.save()

            # Prepare success response
            response_data = {
                "message": "Your profile has been updated!",
                "user_id": user.id,
                "name": user.name,
                "phone_number": user.phone_number,
                "address": user.address,
                "profile_picture": (
                    user.profile_picture.url if user.profile_picture else None
                ),
                # Add more fields as needed
            }

            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON format."}, status=status.HTTP_400_BAD_REQUEST
            )

        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return JsonResponse(
                {"error": "Internal Server Error: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    else:
        return JsonResponse(
            {"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


# Update Api Ends
