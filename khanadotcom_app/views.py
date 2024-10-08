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
    EmailsLogs,
    ContactMessage,
    Review,
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


from datetime import datetime
from rest_framework_simplejwt.tokens import AccessToken


@csrf_exempt
@api_view(["POST"])
def login_api(request):
    if request.method == "POST":
        username = request.data.get("email")
        password = request.data.get("password")

        # Authenticate the user
        user = authenticate(username=username, password=password)
        if user is not None:
            # Reset failed login attempts on successful login
            FailedLoginAttempt.objects.filter(user=user).delete()
            login(request, user)

            # Check if the existing token is valid
            if user.access_token:
                try:
                    # Decode the token to check its validity
                    access_token = AccessToken(user.access_token)
                    if access_token["exp"] > datetime.now().timestamp():
                        return Response(
                            {
                                "success": "Login successful.",
                                "access_token": user.access_token,
                                "user_type": user.user_type,
                            }
                        )
                except Exception as e:
                    # Token is invalid, so generate a new one
                    pass

            # If token is not valid or not present, generate a new one
            try:
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token

                # Save the access token to the user's record
                user.access_token = str(access_token)
                user.save()

                return Response(
                    {
                        "success": "Login successful.",
                        "access_token": str(access_token),
                        "user_type": user.user_type,
                    }
                )
            except Exception as e:
                return Response(
                    {"error": "Error generating token: " + str(e)},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

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
    try:
        mail_subject = "Activate Your Account"
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

        # Log email in EmailsLogs table
        EmailsLogs.objects.create(
            subject=mail_subject,
            message=message,
            recipient=to_email,
            sent_date=timezone.now(),
            added_by=user,
            is_otp=0,
        )

    except Exception as e:
        # Handle exceptions or errors here, such as logging them or notifying admins
        print(f"Failed to send activation email: {str(e)}")
        raise  # Raise the exception to propagate it if needed


@api_view(["POST"])
def change_pass_api(request):
    try:
        user = request.user
        data = request.data

        # Retrieve passwords from the request data
        current_password = data.get("current_password")
        new_password = data.get("new_password")

        # Check if the current password is provided
        if not current_password:
            return Response(
                {"error": "Current password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Authenticate the user with the current password
        if not user.check_password(current_password):
            return Response(
                {"error": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the new password is provided
        if not new_password:
            return Response(
                {"error": "New password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate the new password
        try:
            validate_password(new_password)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password
        user.set_password(new_password)
        user.save()

        return Response(
            {"success": "Password has been changed successfully."},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "An error occurred: " + str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# authentication ends


# Basic apis starts


# @permission_classes([IsAuthenticated])
@api_view(["GET"])
def owner_profile_api(request):
    user = request.user
    profile_picture_url = None
    if user.profile_picture:
        if user.profile_picture.url:
            profile_picture_url = user.profile_picture.url

    # Base user data
    data = {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "user_type": user.user_type,
        "name": user.name,
        "phone_number": user.phone_number,
        "address": user.address,
        "profile_picture": profile_picture_url,
    }
    restaurant_owner = get_object_or_404(RestaurantOwner, user=user)
    data.update(
        {
            "aadhaar_card_number": restaurant_owner.aadhaar_card_number,
        }
    )

    return Response(data, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def delivery_person_profile_api(request):
    user = request.user
    profile_picture_url = None
    if user.profile_picture:
        if user.profile_picture.url:
            profile_picture_url = user.profile_picture.url
    # Base user data
    data = {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "user_type": user.user_type,
        "name": user.name,
        "phone_number": user.phone_number,
        "address": user.address,
        "profile_picture": profile_picture_url,
    }
    delivery_person = get_object_or_404(DeliveryPerson, user=user)
    data.update(
        {
            "aadhaar_card_number": delivery_person.aadhaar_card_number,
            "vehicle_details": delivery_person.vehicle_details,
            "availability_status": delivery_person.availability_status,
            "rating": delivery_person.rating,
        }
    )

    return Response(data, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def user_profile_api(request):
    user = request.user
    profile_picture_url = None
    if user.profile_picture:
        if user.profile_picture.url:
            profile_picture_url = user.profile_picture.url
    # Base user data
    data = {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "user_type": user.user_type,
        "name": user.name,
        "phone_number": user.phone_number,
        "address": user.address,
        "profile_picture": profile_picture_url,
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def restaurant_list_api(request):
    restaurants = Restaurant.objects.all()
    data = [
        {
            "id": restaurant.restaurant_id,
            "name": restaurant.name,
            "image": restaurant.profile_pic.url,
            "rating": restaurant.rating,
            "description": restaurant.description,
        }
        for restaurant in restaurants
    ]
    return Response(data)


@api_view(["GET"])
def restaurant_detail_api(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    data = {
        "id": restaurant.restaurant_id,
        "name": restaurant.name,
        "rating": restaurant.rating,
        "description": restaurant.description,
        "image": restaurant.profile_pic.url,
        "address": restaurant.address,
        "phone_number": restaurant.phone_number,
        "email": restaurant.email,
        "restaurant_GST": restaurant.restaurant_GST,
    }
    return Response(data)


@api_view(["GET"])
def menu_items_api_by_restaurant(request, restaurant_id):
    menu_items = MenuItem.objects.filter(restaurant_id=restaurant_id)
    data = [
        {
            "id": item.menu_item_id,
            "name": item.name,
            "restaurant": item.restaurant.name,
            "restaurant_id": item.restaurant.restaurant_id,
            "price": item.price,
            "description": item.description,
            "image": item.menu_item_pic.url,
            "availability": item.availability,
            "rating": item.rating,
            "preparation_time": item.preparation_time,
        }
        for item in menu_items
    ]
    return Response(data)


@api_view(["GET"])
def menu_items_api(request):
    menu_items = MenuItem.objects.all()
    data = [
        {
            "id": item.menu_item_id,
            "name": item.name,
            "restaurant": item.restaurant.name,
            "restaurant_id": item.restaurant.restaurant_id,
            "price": item.price,
            "description": item.description,
            "image": item.menu_item_pic.url,
            "availability": item.availability,
            "rating": item.rating,
            "preparation_time": item.preparation_time,
        }
        for item in menu_items
    ]
    return Response(data)


# Basic api ends


# Update Api Starts


@permission_classes([IsAuthenticated])
@api_view(["PUT"])
def update_profile_picture_api(request):
    user = request.user

    if "profile_picture" not in request.FILES:
        return Response(
            {"error": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST
        )

    profile_picture = request.FILES["profile_picture"]

    # Update user's profile picture
    user.profile_picture = profile_picture
    user.save()

    return Response(
        {"message": "Profile picture updated successfully"}, status=status.HTTP_200_OK
    )


@permission_classes([IsAuthenticated])
@api_view(["PUT"])
def update_owner_profile_api(request):
    user = request.user
    restaurant_owner = get_object_or_404(RestaurantOwner, user=user)

    # Update base user data
    user_data = {
        "username": request.data.get("username", user.username),
        "email": user.email,
        "name": request.data.get("name", user.name),
        "phone_number": request.data.get("phone_number", user.phone_number),
        "address": request.data.get("address", user.address),
    }
    owner_data = {
        "aadhaar_card_number": restaurant_owner.aadhaar_card_number,
    }

    # Update user and owner information
    for attr, value in user_data.items():
        setattr(user, attr, value)
    user.save()
    for attr, value in owner_data.items():
        setattr(restaurant_owner, attr, value)
    restaurant_owner.save()

    return Response(
        {"message": "Profile updated successfully"}, status=status.HTTP_200_OK
    )


@permission_classes([IsAuthenticated])
@api_view(["PUT"])
def update_delivery_person_profile_api(request):
    user = request.user
    delivery_person = get_object_or_404(DeliveryPerson, user=user)

    # Update base user data
    user_data = {
        "username": request.data.get("username", user.username),
        "email": user.email,
        "name": request.data.get("name", user.name),
        "phone_number": request.data.get("phone_number", user.phone_number),
        "address": request.data.get("address", user.address),
    }

    # Update additional delivery person-specific data
    delivery_person_data = {
        "aadhaar_card_number": delivery_person.aadhaar_card_number,
        "vehicle_details": request.data.get(
            "vehicle_details", delivery_person.vehicle_details
        ),
        "availability_status": request.data.get(
            "availability_status", delivery_person.availability_status
        ),
        "rating": delivery_person.rating,
    }

    # Update user and delivery person information
    for attr, value in user_data.items():
        setattr(user, attr, value)
    user.save()

    for attr, value in delivery_person_data.items():
        setattr(delivery_person, attr, value)
    delivery_person.save()

    return Response(
        {"message": "Profile updated successfully"}, status=status.HTTP_200_OK
    )


@permission_classes([IsAuthenticated])
@api_view(["PUT"])
def update_user_profile_api(request):
    user = request.user

    # Update base user data
    user_data = {
        "username": request.data.get("username", user.username),
        "email": user.email,
        "name": request.data.get("name", user.name),
        "phone_number": request.data.get("phone_number", user.phone_number),
        "address": request.data.get("address", user.address),
    }

    # Update user information
    for attr, value in user_data.items():
        setattr(user, attr, value)
    user.save()

    return Response(
        {"message": "Profile updated successfully"}, status=status.HTTP_200_OK
    )


# Update Api Ends

# Delete api  Starts


@api_view(["DELETE"])
def delete_user_api(request, user_id):
    try:
        user = get_object_or_404(User, user_id=user_id)

        # Soft delete the user
        user.is_deleted = True
        user.save()

        # Soft delete specific table data based on user type
        if user.user_type == "restaurant_owner":
            restaurant_owner = get_object_or_404(RestaurantOwner, user=user)
            restaurant_owner.is_deleted = True
            restaurant_owner.save()
        elif user.user_type == "delivery_person":
            delivery_person = get_object_or_404(DeliveryPerson, user=user)
            delivery_person.is_deleted = True
            delivery_person.save()
        elif user.user_type == "customer":
            customer_detail = get_object_or_404(CustomerDetail, user=user)
            customer_detail.is_deleted = True
            customer_detail.save()

        return Response(
            {"success": "User and associated data soft deleted successfully."},
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response(
            {"error": f"Failed to soft delete user: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Delete api  Ends

#  reset password api start


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

# contact us start


@api_view(["POST"])
def contact_us(request):
    if request.method == "POST":
        try:
            data = request.data  # Use request.data to handle JSON payload
            name = data["name"]
            email = data["email"]
            message = data["message"]

            contact_message = ContactMessage(name=name, email=email, message=message)
            contact_message.save()

            return JsonResponse({"message": "Your message is sent"})

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


# contact us end

# Orde rplacement and validation start
# Order placement api Starts


@permission_classes([IsAuthenticated])
@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def order_placement_api(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    user = request.user
    if request.method == "POST":
        data = request.data

        # Extract data from request body
        delivery_address = user.address
        items = data.get("items", [])

        # Validate data presence
        if not (items):
            return Response(
                {"error": "items are required fields."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create Order object
        order = Order.objects.create(
            user=user,
            delivery_address=delivery_address,
            total_amount=0,
        )

        # Process each selected menu item
        total_amount = 0

        for item in items:
            menu_item = get_object_or_404(MenuItem, pk=item["item_id"])
            quantity = item["quantity"]
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
        # notify_restaurant_owner(order)

        # Return JSON response with order confirmation details
        return Response(
            {
                "success": "Order placed successfully.",
                "user_id": user.user_id,
                "restaurant_id": restaurant.restaurant_id,
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


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def confirm_order(request, order_id):
    user = request.user

    # Check if the user is a restaurant owner
    if user.user_type != "restaurant_owner":
        return Response(
            {"error": "Only restaurant owners can confirm or reject orders."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Get the order object
    order = get_object_or_404(Order, pk=order_id)
    status_update = request.data.get("status")

    if status_update not in ["confirmed", "rejected"]:
        return Response(
            {
                "error": "Invalid status. Status should be either 'confirmed' or 'rejected'."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Update the order status
    order.order_status = status_update
    if status_update == "rejected":
        order.order_status = "cancelled"
        order.is_deleted = True

    order.save()

    return Response(
        {"success": f"Order has been {status_update}."},
        status=status.HTTP_200_OK,
    )


# Order placement api Ends


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_order_status_api(request, order_id):
    try:
        order = get_object_or_404(Order, pk=order_id)
        order_status = {
            "order_id": order.id,
            "status": order.status,
        }
        return Response(order_status, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": f"Internal Server Error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@permission_classes([IsAuthenticated])
@api_view(["PUT"])
def update_order_status_to_preparing(request, order_id):
    try:
        user = request.user

        # Check if the user is a restaurant owner
        if user.user_type != "restaurant_owner":
            return Response(
                {"error": "Only restaurant owners can Start preparing the dish."},
                status=status.HTTP_403_FORBIDDEN,
            )
        order = get_object_or_404(Order, pk=order_id)
        order.status = "Preparing"
        order.save()
        return Response(
            {"message": "Order status updated to Preparing."}, status=status.HTTP_200_OK
        )
    except Order.DoesNotExist:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": f"Internal Server Error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def assign_order_to_delivery_person(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    if order.order_status == "confirmed":
        success = order.assign_delivery_person()
        if success:
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Delivery person assigned successfully.",
                }
            )
        else:
            return JsonResponse(
                {"status": "error", "message": "No available delivery person."}
            )
    else:
        return JsonResponse(
            {"status": "error", "message": "Order is not in confirmed status."}
        )


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def order_history_api(request):
    # Fetch orders for the current user (assuming user is authenticated)
    orders = Order.objects.filter(user=request.user).order_by("-order_date")

    # Serialize queryset into JSON data
    serializer = OrderSerializer(orders, many=True)

    return Response(serializer.data)


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def add_restaurant_api(request):
    user = request.user
    if request.method == "POST":
        try:
            # Check if the user is a restaurant owner
            if user.user_type != "restaurant_owner":
                return JsonResponse(
                    {"error": "Only restaurant owners can add a restaurant."},
                    status=403,
                )

            data = request.data
            name = data.get("name")
            address = data.get("address")
            phone_number = data.get("phone_number")
            email = data.get("email")
            description = data.get("description")
            restaurant_GST = data.get("restaurant_GST")
            profile_pic = request.FILES.get("profile_pic")

            # Validate required fields
            if not all(
                [
                    name,
                    address,
                    phone_number,
                    email,
                    description,
                    restaurant_GST,
                    profile_pic,
                ]
            ):
                return JsonResponse({"error": "All fields are required."}, status=400)

            # Ensure the restaurant owner's profile exists
            try:
                owner = RestaurantOwner.objects.get(user=user)
                owner = get_object_or_404(
                    RestaurantOwner, restaurant_owner_id=owner.restaurant_owner_id
                )

            except RestaurantOwner.DoesNotExist:
                return JsonResponse(
                    {"error": "Restaurant owner profile not found."}, status=404
                )

            # Create restaurant
            restaurant = Restaurant.objects.create(
                owner=owner,
                name=name,
                address=address,
                phone_number=phone_number,
                email=email,
                description=description,
                restaurant_GST=restaurant_GST,
            )

            # Handle profile picture if provided
            if profile_pic:
                ext = profile_pic.name.split(".")[-1]
                new_image_name = f"{restaurant.restaurant_id}.{ext}"
                profile_pic.name = new_image_name
                restaurant.profile_pic.save(new_image_name, profile_pic)

            return JsonResponse(
                {
                    "success": "Restaurant created successfully.",
                    "restaurant_id": restaurant.restaurant_id,
                },
                status=201,
            )

        except Exception as e:
            return JsonResponse({"error": f"Error: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def add_menu_item_api(request):
    user = request.user
    if request.method == "POST":
        data = request.data
        name = data.get("name")
        description = data.get("description")
        price = data.get("price")
        preparation_time = data.get("preparation_time")
        menu_item_pic = request.FILES.get("menu_item_pic")
        restaurant_id = data.get("restaurant_id")
        if not all(
            [name, description, price, preparation_time, restaurant_id, menu_item_pic]
        ):
            return JsonResponse({"error": "All fields are required."}, status=400)
        try:
            restaurant = get_object_or_404(Restaurant, restaurant_id=restaurant_id)
            if restaurant.owner.user != user:
                return JsonResponse(
                    {
                        "error": "You are not authorized to add items to this restaurant."
                    },
                    status=403,
                )

            menu = MenuItem.objects.create(
                restaurant=restaurant,
                name=name,
                description=description,
                price=price,
                preparation_time=preparation_time,
            )
            if menu_item_pic:
                ext = menu_item_pic.name.split(".")[-1]
                new_image_name = f"{menu.menu_item_id}.{ext}"
                menu_item_pic.name = new_image_name
                menu.menu_item_pic.save(new_image_name, menu_item_pic)

            return JsonResponse(
                {
                    "success": "Menu Item created successfully.",
                    "menu_item_id": menu.menu_item_id,
                },
                status=201,
            )

        except Exception as e:
            return JsonResponse({"error": f"Error: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)


# Adding ends for Owner

# Rating apis

from django.db.models import Avg


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rate_restaurant_api(request, restaurant_id):
    user = request.user

    # Check if the user is a customer
    if user.user_type != "customer":
        return JsonResponse(
            {"error": "Only customers can rate restaurants."}, status=403
        )

    if request.method == "POST":
        data = request.data
        rating_value = data.get("rating")
        comment = data.get("comment")

        # Validate rating value and restaurant_id
        if not all([restaurant_id, rating_value]):
            return JsonResponse(
                {"error": "Restaurant ID and rating value are required."}, status=400
            )

        try:
            rating_value = float(rating_value)
            if rating_value < 1 or rating_value > 5:
                return JsonResponse(
                    {"error": "Rating value must be between 1 and 5."}, status=400
                )
        except ValueError:
            return JsonResponse({"error": "Invalid rating value."}, status=400)

        # Get the restaurant
        restaurant = get_object_or_404(Restaurant, restaurant_id=restaurant_id)

        try:
            # Check if the user has already rated this restaurant
            existing_rating = Review.objects.filter(
                user=user, restaurant=restaurant
            ).first()

            if existing_rating:
                # Update the existing rating
                existing_rating.rating = rating_value
                existing_rating.comment = comment
                existing_rating.save()
                message = "Rating updated successfully."
            else:
                # Create a new rating
                Review.objects.create(
                    user=user,
                    restaurant=restaurant,
                    rating=rating_value,
                    comment=comment,
                )
                message = "Rating submitted successfully."

            # Calculate the new average rating for the restaurant
            avg_rating = Review.objects.filter(restaurant=restaurant).aggregate(
                Avg("rating")
            )["rating__avg"]
            restaurant.rating = round(
                avg_rating, 2
            )  # Update the restaurant's rating with the new average
            restaurant.save()

            return JsonResponse(
                {
                    "success": message,
                    "new_rating": rating_value,
                    "restaurant_average_rating": restaurant.rating,
                },
                status=200,
            )

        except Exception as e:
            return JsonResponse({"error": f"Error: {str(e)}"}, status=500)

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rate_menu_item_api(request, menu_item_id):
    user = request.user

    # Check if the user is a customer
    if user.user_type != "customer":
        return JsonResponse(
            {"error": "Only customers can rate menu items."}, status=403
        )

    if request.method == "POST":
        data = request.data
        rating_value = data.get("rating")
        comment = data.get("comment")

        # Validate rating value and menu_item_id
        if not all([menu_item_id, rating_value]):
            return JsonResponse(
                {"error": "Menu item ID and rating value are required."}, status=400
            )

        try:
            rating_value = float(rating_value)
            if rating_value < 1 or rating_value > 5:
                return JsonResponse(
                    {"error": "Rating value must be between 1 and 5."}, status=400
                )
        except ValueError:
            return JsonResponse({"error": "Invalid rating value."}, status=400)

        # Get the menu item
        menu_item = get_object_or_404(MenuItem, pk=menu_item_id)

        try:
            # Check if the user has already rated this menu item
            existing_rating = Review.objects.filter(
                user=user, menu_item=menu_item
            ).first()

            if existing_rating:
                # Update the existing rating
                existing_rating.rating = rating_value
                existing_rating.comment = comment
                existing_rating.save()
                message = "Rating updated successfully."
            else:
                # Create a new rating
                Review.objects.create(
                    user=user,
                    menu_item=menu_item,
                    rating=rating_value,
                    comment=comment,
                )
                message = "Rating submitted successfully."

            # Calculate the new average rating for the menu item
            avg_rating = Review.objects.filter(menu_item=menu_item).aggregate(
                Avg("rating")
            )["rating__avg"]
            menu_item.rating = round(
                avg_rating, 2
            )  # Update the menu item's rating with the new average
            menu_item.save()

            return JsonResponse(
                {
                    "success": message,
                    "new_rating": rating_value,
                    "menu_item_average_rating": menu_item.rating,
                },
                status=200,
            )

        except Exception as e:
            return JsonResponse({"error": f"Error: {str(e)}"}, status=500)

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rate_delivery_person_api(request, delivery_person_id):
    user = request.user

    # Check if the user is a customer
    if user.user_type != "customer":
        return JsonResponse(
            {"error": "Only customers can rate delivery persons."}, status=403
        )

    if request.method == "POST":
        data = request.data
        rating_value = data.get("rating")
        comment = data.get("comment")

        # Validate rating value and delivery_person_id
        if not all([delivery_person_id, rating_value]):
            return JsonResponse(
                {"error": "Delivery person ID and rating value are required."},
                status=400,
            )

        try:
            rating_value = float(rating_value)
            if rating_value < 1 or rating_value > 5:
                return JsonResponse(
                    {"error": "Rating value must be between 1 and 5."}, status=400
                )
        except ValueError:
            return JsonResponse({"error": "Invalid rating value."}, status=400)

        # Get the delivery person
        delivery_person = get_object_or_404(DeliveryPerson, pk=delivery_person_id)

        try:
            # Check if the user has already rated this delivery person
            existing_rating = Review.objects.filter(
                user=user, delivery_person=delivery_person
            ).first()

            if existing_rating:
                # Update the existing rating
                existing_rating.rating = rating_value
                existing_rating.comment = comment
                existing_rating.save()
                message = "Rating updated successfully."
            else:
                # Create a new rating
                Review.objects.create(
                    user=user,
                    delivery_person=delivery_person,
                    rating=rating_value,
                    comment=comment,
                )
                message = "Rating submitted successfully."

            # Calculate the new average rating for the delivery person
            avg_rating = Review.objects.filter(
                delivery_person=delivery_person
            ).aggregate(Avg("rating"))["rating__avg"]
            delivery_person.rating = round(
                avg_rating, 2
            )  # Update the delivery person's rating with the new average
            delivery_person.save()

            return JsonResponse(
                {
                    "success": message,
                    "new_rating": rating_value,
                    "delivery_person_average_rating": delivery_person.rating,
                },
                status=200,
            )

        except Exception as e:
            return JsonResponse({"error": f"Error: {str(e)}"}, status=500)

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)


# Rating end
