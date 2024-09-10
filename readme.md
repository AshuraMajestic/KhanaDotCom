Here is the updated documentation for your Restaurant Management Django REST API:

---

# Restaurant Management Django REST API

This Django project implements a REST API for managing restaurants, users, orders, and authentication.

## API Endpoints

### Authentication

#### 1. **Signup**
- **URL:** `/signup/`
- **Method:** POST
- **Description:** Allows users to register with the system. Requires username, email, password, and user type (restaurant owner or delivery person).
- **Parameters:**
  - `username` (string, required)
  - `name` (string, required)
  - `phone_number` (string, required)
  - `address` (string, required)
  - `email` (string, required)
  - `password` (string, required)
  - `user_type` (string, required)
  - `aadhaar_number` (string, optional)
  - `date_of_birth` (date, optional)
  - `vehicle_details` (string, optional, for delivery person)
- **Response:** Returns JSON with success message or error.
- **Example:**
  ```json
  {
    "username": "abhishek",
    "name": "Abhishek",
    "phone_number": "3456786578",
    "address": "Gujarat",
    "email": "kushvahaabhisek33@gmail.com",
    "password": "abc",
    "user_type": "customer",
    "date_of_birth": "1990-01-01"
  }
  ```

  ```json
  {
    "username": "delivery123",
    "name": "Delivery Person",
    "phone_number": "3456786578",
    "address": "Gujarat",
    "email": "delivery@example.com",
    "password": "securepassword",
    "user_type": "delivery_person",
    "aadhaar_number": "123456789012",
    "vehicle_details": "Bike"
  }
  ```

  ```json
  {
    "username": "owner123",
    "name": "Owner Name",
    "phone_number": "3456786578",
    "address": "Gujarat",
    "email": "owner@example.com",
    "password": "securepassword",
    "user_type": "restaurant_owner",
    "aadhaar_number": "1234 5678 9101"
  }
  ```

#### 2. **Login**
- **URL:** `/login/`
- **Method:** POST
- **Description:** Allows users to authenticate.
- **Parameters:**
  - `email` (string, required)
  - `password` (string, required)
- **Response:** Returns JSON with access token,user_type and sucess message or error message.

#### 3. **Logout**
- **URL:** `/logout/`
- **Method:** POST
- **Description:** Logs out the currently authenticated user.Also remove the jwt token from the local database
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Response:** Returns JSON with success message.

### 4. User Profile


### i. **User Profile API**

- **URL:** `/profile-user/`
- **Method:** `GET`
- **Description:** Retrieves the profile information of the currently authenticated user.
- **Authorization:** Bearer Token (required)
  - **Header Example:** `'Authorization': 'Bearer <your_access_token>'`
- **Response:**
  - **Status:** `200 OK`
  - **Content-Type:** `application/json`
  - **Body Example:**
    ```json
    {
      "username": "john_doe",
      "email": "john@example.com",
      "user_type": "customer",
      "name": "John Doe",
      "phone_number": "+1234567890",
      "address": "123 Main St, Springfield"
      "profile-picture":null || "/media/profile_p[ictur.png]"
    }
    ```

### ii. **Owner Profile API**

- **URL:** `/profile-owner/`
- **Method:** `GET`
- **Description:** Retrieves the profile information of the currently authenticated restaurant owner.
- **Authorization:** Bearer Token (required)
  - **Header Example:** `'Authorization': 'Bearer <your_access_token>'`
- **Response:**
  - **Status:** `200 OK`
  - **Content-Type:** `application/json`
  - **Body Example:**
    ```json
    {
      "username": "owner_jane",
      "email": "jane@example.com",
      "user_type": "restaurant_owner",
      "name": "Jane Smith",
      "phone_number": "+1234567890",
      "address": "456 Elm St, Springfield",
      "aadhaar_card_number": "1234-5678-9012"
      "profile-picture":null || "/media/profile_p[ictur.png]"
    }
    ```

### iii. **Delivery Person Profile API**

- **URL:** `/profile-delivery-person/`
- **Method:** `GET`
- **Description:** Retrieves the profile information of the currently authenticated delivery person.
- **Authorization:** Bearer Token (required)
  - **Header Example:** `'Authorization': 'Bearer <your_access_token>'`
- **Response:**
  - **Status:** `200 OK`
  - **Content-Type:** `application/json`
  - **Body Example:**
    ```json
    {
      "username": "delivery_jake",
      "email": "jake@example.com",
      "user_type": "delivery_person",
      "name": "Jake Doe",
      "phone_number": "+1234567890",
      "address": "789 Oak St, Springfield",
      "aadhaar_card_number": "5678-1234-9012",
      "vehicle_details": "Bike - XYZ123",
      "availability_status": "Available",
      "profile-picture":null || "/media/profile_p[ictur.png]"
      "rating": 4.8
    }
    ```


### Restaurant Management

#### 5. **List Restaurants**
- **URL:** `/api/restaurants/`
- **Method:** GET
- **Description:** Retrieves a list of all restaurants.
- **Response:** Returns JSON array of restaurant objects with id and name.

#### 6. **Restaurant Detail**
- **URL:** `/api/restaurants/<restaurant_id>/`
- **Method:** GET
- **Description:** Retrieves details of a specific restaurant.
- **Parameters:**
  - `restaurant_id` (integer, required)
- **Response:** Returns JSON object with restaurant id, name, description and image.

#### 7. **Menu Items**
- **URL:** `/api/restaurants/<restaurant_id>/menu/`
- **Method:** GET
- **Description:** Retrieves menu items for a specific restaurant.
- **Parameters:**
  - `restaurant_id` (integer, required)
- **Response:** Returns JSON array of menu item objects with id, name,description,image, restaurant,restaurant_id,availabilty,rating,preparation and price.

#### 7. **Menu Items**
- **URL:** `/api/menu/`
- **Method:** GET
- **Description:** Retrieves all menu items.
- **Parameters:**
  - None
- **Response:** Returns JSON array of menu item objects with id, name,description,image, restaurant,restaurant_id,availabilty,rating,preparation and price.
"restaurant": "White Bricks",
"restaurant_id": 23,
"price": 500.0,
"description": "Pizza with lots of cheez and cold drink",
"image": "/media/menu_items/25.png",
"availability": true,
"rating": 0.0,
"preparation_time": 20


### Update User Details

#### 8. **Update Details User**
- **URL:** `/update-profile-user/`
- **Method:** PUT
- **Description:** Updates details of the currently authenticated customer
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`

- **Request Body:**

  ```json
  {
   "username": "username",
        "name": "name",
        "phone_number": "1234567890",
        "address": "address",
  }
  ```

- **Response:** Returns Update successful message, or error messages.

#### 9. **Update Details Owner**
- **URL:** `/update-profile-owner/`
- **Method:** PUT
- **Description:** Updates details of the currently authenticated owner
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`

- **Request Body:**

  ```json
  {
        "username": "username",
        "name": "name",
        "phone_number": "1234567890",
        "address": "address",
  }
  ```

- **Response:** Returns Update successful message, or error messages.

#### 10. **Update Details Delivery Person**
- **URL:** `/update-profile-delivery-person/`
- **Method:** PUT
- **Description:** Updates details of the currently authenticated customer
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`

- **Request Body:**

  ```json
  {
        "username": "username",
        "name": "name",
        "phone_number": "1234567890",
        "address": "address",
        "vehicle_details": "GJ181234",
        "availability_status": True,
  }
  ```

- **Response:** Returns Update successful message, or error messages.

#### 11. **Delete User**
- **URL:** `/delete-user/<int:user_id>/`
- **Method:** DELETE
- **Description:** Soft Delete the user in database
- **Request Parameters:** Need User id in the url
- **Response:** Returns Success or error

## Password Reset Using Django Views and Templates

### 12. Request Password Reset

- **URL:** `/password-reset/`
- **Method:** POST
- **Description:** Initiates a password reset process by sending a password reset email to the user's registered email address.

#### Request Body
```json
{
    "email": "user@example.com"
}
```

#### Responses
- **Success Response:** HTTP 200 OK
  ```json
  {
      "success": "Password reset email has been sent."
  }
  ```
  
- **Error Response:** HTTP 400 Bad Request
  ```json
  {
      "error": "Email is required."
  }
  ```
  ```json
  {
      "error": "No user found with this email."
  }
  ```


#### 13. **Contact**
- **URL:** `/contact/`
- **Method:** POST
- **Description:** Allows users to authenticate.
- **Parameters:**
  - `name` (string, required)
  - `email` (string, required)
  - `message` (string, required)
- **Response:** Returns JSON with message "Message successfully sent"

### Order Management

#### 14. **Place Order**
- **URL:** `restaurants/<int:restaurant_id>/order/`
- **Method:** POST
- **Description:** Allows placing an order at a specific restaurant.
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Parameters:**
  - `restaurant_id` (integer, required)
- **Request Body:**
  ```json
  {
    "items": [
      {
        "item_id": 1(menu_item_id),
        "quantity": 2
      },
      {
        "item_id": 5(menu_item_id),
        "quantity": 1
      }
    ]
  }
  ```
- **Response:** Returns JSON with order details including order id and total amount.

#### 15. **Order Confirmation**
- **URL:** `/order/<order_id>/`
- **Method:** POST
- **Description:** Accept or reject a order by Restaurant owner.
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Parameters:**
  - `order_id` (string, required) in url
  - `status` (string,required)
- **Response:** Returns JSON with successfull acceptance or rejection message.

#### 16. **Order Status**
- **URL:** `order/status/<str:order_id>/`
- **Method:** GET
- **Description:** Get Status of Order
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Parameters:**
  - `order_id` (string, required) in url
- **Response:** Returns JSON with order id and status

#### 17. **Start Preparing Order**
- **URL:** `order/<str:order_id>/prepare/`
- **Method:** POST
- **Description:** Start Preparing order and change status
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Parameters:**
  - `order_id` (string, required) in url
- **Response:** Returns JSON with message or error

#### 18. **Assign Order to Delivery Person**
- **URL:** `assign_order/<int:order_id>/`
- **Method:** POST
- **Description:** Assign a delivery person to a confirmed order.
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Parameters:**
  - `order_id` (string, required) in URL
- **Response:** Returns JSON with status and message.

**Request Example:**
```http
POST /order/<order_id>/assign_delivery/
Authorization: Bearer <your_access_token>
```

**Response Examples:**

- **Success Response:**
  ```json
  {
    "status": "success",
    "message": "Delivery person assigned successfully."
  }
  ```

- **Error Response (Order not in confirmed status):**
  ```json
  {
    "status": "error",
    "message": "Order is not in confirmed status."
  }
  ```

- **Error Response (No available delivery person):**
  ```json
  {
    "status": "error",
    "message": "No available delivery person."
  }
  ```


#### 19. **Order History**
- **URL:** `/orders/history/`
- **Method:** GET
- **Description:** Retrieves order history for the currently authenticated user.
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Response:** Returns JSON array of order objects with order id, total amount, and order date.


Sure, I'll include example requests and responses for each API.

### API Documentation with Examples

---

#### **20. Add Restaurant API**

**Endpoint:** `/add-restaurant/`  
**Method:** `POST`  
**Permissions Required:** Authentication (Only accessible to authenticated restaurnant owner)  

**Description:**  
This API endpoint allows restaurant owners to add a new restaurant to the system. It requires the user to be authenticated and have a user type of "restaurant_owner."

**Request Parameters:**

- **name** (string): The name of the restaurant. (Required)
- **address** (string): The address of the restaurant. (Required)
- **phone_number** (string): The phone number of the restaurant. (Required)
- **email** (string): The email address of the restaurant. (Required)
- **description** (string): A description of the restaurant. (Required)
- **restaurant_GST** (string): The GST number of the restaurant. (Required)
- **profile_pic** (file): An optional profile picture of the restaurant.

**Example Request:**

```http
POST /add-restaurant/
Authorization: Bearer <your_token>
Content-Type: multipart/form-data

{
  "name": "The Gourmet Bistro",
  "address": "123 Foodie Lane, Flavor Town",
  "phone_number": "+1234567890",
  "email": "contact@gourmetbistro.com",
  "description": "A bistro offering a wide range of gourmet dishes.",
  "restaurant_GST": "12ABCDE3456F7Z8",
  "profile_pic": (file: gourmet_bistro.jpg)
}
```

**Example Response (Success):**

```json
{
  "success": "Restaurant created successfully.",
  "restaurant_id": 1
}
```

**Example Response (Error - Missing Field):**

```json
{
  "error": "All fields are required."
}
```

**Example Response (Error - Unauthorized):**

```json
{
  "error": "Only restaurant owners can add a restaurant."
}
```

**Example Response (Error - Owner Profile Not Found):**

```json
{
  "error": "Restaurant owner profile not found."
}
```

**Example Response (Error - Server Issue):**

```json
{
  "error": "Error: Description of the error"
}
```

---

#### **21. Add Menu Item API**

**Endpoint:** `/add-menu-items/`  
**Method:** `POST`  
**Permissions Required:** Authentication (Only accessible to authenticated users)  

**Description:**  
This API endpoint allows authenticated restaurant owners to add a new menu item to their restaurant. It ensures that the user is the owner of the restaurant before allowing the addition of a menu item.

**Request Parameters:**

- **name** (string): The name of the menu item. (Required)
- **description** (string): A description of the menu item. (Required)
- **price** (decimal): The price of the menu item. (Required)
- **preparation_time** (string): The preparation time for the menu item. (Required)
- **menu_item_pic** (file): An optional picture of the menu item.
- **restaurant_id** (integer): The ID of the restaurant where the menu item will be added. (Required)

**Example Request:**

```http
POST /add-menu-item/
Authorization: Bearer <your_token>
Content-Type: multipart/form-data

{
  "name": "Truffle Risotto",
  "description": "Creamy risotto with truffle oil and mushrooms.",
  "price": 19.99,
  "preparation_time": "20",(In minutes)
  "menu_item_pic": (file: truffle_risotto.jpg),
  "restaurant_id": 1
}
```

**Example Response (Success):**

```json
{
  "success": "Menu Item created successfully.",
  "menu_item_id": 101
}
```

**Example Response (Error - Missing Field):**

```json
{
  "error": "All fields are required."
}
```

**Example Response (Error - Unauthorized):**

```json
{
  "error": "You are not authorized to add items to this restaurant."
}
```

**Example Response (Error - Server Issue):**

```json
{
  "error": "Error: Description of the error"
}
```

#### 22. **Change Password**
- **URL:** `/change-password/`
- **Method:** POST
- **Description:** Allows authenticated users to change their password. Requires the current password for verification and a new password.
- **Parameters:**
  - `current_password` (string, required): The user's current password.
  - `new_password` (string, required): The new password that the user wants to set.
- **Response:** Returns JSON with a success message if the password is changed successfully, or an error message if the process fails.
- **Authentication:** The user must be authenticated (e.g., via a session or a token).
- **Example:**
  ```json
  {
    "current_password": "old_password123",
    "new_password": "NewPassword!456"
  }
  ```
- **Response Examples:**
  - **Success:**
    ```json
    {
      "success": "Password has been changed successfully."
    }
    ```
  - **Error:**
    ```json
    {
      "error": "Current password is incorrect."
    }
    ```


### **Rating API Documentation**

#### 23. **Rate Restaurant API**

**Endpoint:** `/restaurants/<int:restaurant_id>/rate`  
**Method:** `POST`  
**Permissions Required:** Authentication (Only accessible to authenticated users of type 'customer')  

**Description:**  
This API allows authenticated customers to rate a restaurant. A customer can provide a rating between 1 and 5, along with an optional comment. If a customer has already rated the restaurant, they can update their existing rating.

**Request Parameters:**

- **rating** (float): The rating value for the restaurant (Required, must be between 1 and 5).
- **comment** (string): An optional comment about the restaurant.

**Example Request:**

```http
POST /restaurants/<int:restaurant_id>/rate/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "rating": 4.5,
  "comment": "Great food and service!"
}
```

**Example Response (Success):**

```json
{
  "success": "Rating submitted successfully.",
  "new_rating": 4.5,
  "restaurant_average_rating": 4.3
}
```

**Example Response (Error - Unauthorized):**

```json
{
  "error": "Only customers can rate restaurants."
}
```

**Example Response (Error - Invalid Rating Value):**

```json
{
  "error": "Rating value must be between 1 and 5."
}
```

---

#### 24. **Rate Menu Item API**

**Endpoint:** `/menu/<int:menu_item_id>/rate`  
**Method:** `POST`  
**Permissions Required:** Authentication (Only accessible to authenticated users of type 'customer')  

**Description:**  
This API allows authenticated customers to rate a specific menu item. A customer can provide a rating between 1 and 5, along with an optional comment. If a customer has already rated the menu item, they can update their existing rating.

**Request Parameters:**

- **rating** (float): The rating value for the menu item (Required, must be between 1 and 5).
- **comment** (string): An optional comment about the menu item.

**Example Request:**

```http
POST /menu/<int:menu_item_id>/rate
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "rating": 5,
  "comment": "Best risotto I've ever had!"
}
```

**Example Response (Success):**

```json
{
  "success": "Rating submitted successfully.",
  "new_rating": 5,
  "menu_item_average_rating": 4.8
}
```

**Example Response (Error - Unauthorized):**

```json
{
  "error": "Only customers can rate menu items."
}
```

**Example Response (Error - Invalid Rating Value):**

```json
{
  "error": "Rating value must be between 1 and 5."
}
```

---

#### 25. **Rate Delivery Person API**

**Endpoint:** `delivery-person/<int:delivery_person_id>/rate`  
**Method:** `POST`  
**Permissions Required:** Authentication (Only accessible to authenticated users of type 'customer')  

**Description:**  
This API allows authenticated customers to rate a delivery person. A customer can provide a rating between 1 and 5, along with an optional comment. If a customer has already rated the delivery person, they can update their existing rating.

**Request Parameters:**

- **rating** (float): The rating value for the delivery person (Required, must be between 1 and 5).
- **comment** (string): An optional comment about the delivery person.

**Example Request:**

```http
POST /delivery-person/<int:delivery_person_id>/rate
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "rating": 4.8,
  "comment": "Quick and polite service!"
}
```

**Example Response (Success):**

```json
{
  "success": "Rating submitted successfully.",
  "new_rating": 4.8,
  "delivery_person_average_rating": 4.6
}
```

**Example Response (Error - Unauthorized):**

```json
{
  "error": "Only customers can rate delivery persons."
}
```

**Example Response (Error - Invalid Rating Value):**

```json
{
  "error": "Rating value must be between 1 and 5."
}
```

#### 26. **Update Profile Picture API**

**Endpoint:** `/edit-user-picture/`  
**Method:** `PUT`  
**Permissions Required:** Authentication (Only accessible to authenticated users)

**Description:**  
This API allows authenticated users to update their profile picture by uploading a new image file. The uploaded file replaces the current profile picture associated with the user's account.

**Request Parameters:**

- **profile_picture** (file): The image file to be uploaded as the new profile picture (Required).

**Example Request:**

```http
PUT /api/user/update-profile-picture/
Authorization: Bearer <your_token>
Content-Type: multipart/form-data

{
  "profile_picture": <file>
}
```

**Example Response (Success):**

```json
{
  "message": "Profile picture updated successfully."
}
```

**Example Response (Error - No Image Provided):**

```json
{
  "error": "No image file provided."
}
```

**Example Response (Error - Unauthorized):**

```json
{
  "detail": "Authentication credentials were not provided."
}
```




---

Make sure to replace `<your_access_token>` placeholders with actual access tokens in your implementation. If you need further adjustments or have more questions, feel free to ask!