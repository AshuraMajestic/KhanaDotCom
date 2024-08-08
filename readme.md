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
- **Response:** Returns JSON with access token and refresh token or error message.

#### 3. **Logout**
- **URL:** `/logout/`
- **Method:** POST
- **Description:** Logs out the currently authenticated user.Also remove the jwt token from the local database
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Response:** Returns JSON with success message.

#### 4. **Token**
- **URL:** `/token/`
- **Method:** POST
- **Description:** Retrieves the access token and refresh token.
- **Parameters:**
  - `email` (string, required)
  - `password` (string, required)
- **Response:** Returns JSON with access token and refresh token.

### 5. User Profile

To enhance the design and organization of the user profile APIs, you can introduce a more consistent and modular structure. Below is the improved design for the API endpoints, including detailed information about the endpoints, request format, and expected responses.

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
      "user_type": "user",
      "name": "John Doe",
      "phone_number": "+1234567890",
      "address": "123 Main St, Springfield"
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
      "user_type": "owner",
      "name": "Jane Smith",
      "phone_number": "+1234567890",
      "address": "456 Elm St, Springfield",
      "aadhaar_card_number": "1234-5678-9012"
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
      "rating": 4.8
    }
    ```


### Restaurant Management

#### 6. **List Restaurants**
- **URL:** `/restaurants/`
- **Method:** GET
- **Description:** Retrieves a list of all restaurants.
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Response:** Returns JSON array of restaurant objects with id and name.

#### 7. **Restaurant Detail**
- **URL:** `/restaurant/<restaurant_id>/`
- **Method:** GET
- **Description:** Retrieves details of a specific restaurant.
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Parameters:**
  - `restaurant_id` (integer, required)
- **Response:** Returns JSON object with restaurant id, name, description and image.

#### 8. **Menu Items**
- **URL:** `/restaurants/<restaurant_id>/menu/`
- **Method:** GET
- **Description:** Retrieves menu items for a specific restaurant.
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Parameters:**
  - `restaurant_id` (integer, required)
- **Response:** Returns JSON array of menu item objects with id, name,description,image and price.


### Update User Details

#### 9. **Update Details User**
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

#### 10. **Update Details Owner**
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

#### 11. **Update Details Delivery Person**
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
#### 9. **Update Details User**
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

#### 10. **Delete User**
- **URL:** `/delete-user/<int:user_id>/`
- **Method:** DELETE
- **Description:** Soft Delete the user in database
- **Request Parameters:** Need User id in the url
- **Response:** Returns Success or error

## Password Reset Using Django Views and Templates

### 11. Request Password Reset

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


#### 12. **Contact**
- **URL:** `/contact/`
- **Method:** POST
- **Description:** Allows users to authenticate.
- **Parameters:**
  - `name` (string, required)
  - `email` (string, required)
  - `message` (string, required)
- **Response:** Returns JSON with message "Message successfully sent"

### Order Management

#### 13. **Place Order**
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
      "delivery_address": "string",
      "items": [item_id1, item_id2, ...]
  }
  ```
- **Response:** Returns JSON with order details including order id and total amount.

#### 14. **Order Confirmation**
- **URL:** `/order/<order_id>/`
- **Method:** POST
- **Description:** Accept or reject a order by Restaurant owner.
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Parameters:**
  - `order_id` (string, required) in url
  - `status` (string,required)
- **Response:** Returns JSON with successfull acceptance or rejection message.

#### 15. **Order Status**
- **URL:** `order/status/<str:order_id>/`
- **Method:** GET
- **Description:** Get Status of Order
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Parameters:**
  - `order_id` (string, required) in url
- **Response:** Returns JSON with order id and status

#### 16. **Start Preparing Order**
- **URL:** `order/<str:order_id>/prepare/`
- **Method:** POST
- **Description:** Start Preparing order and change status
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Parameters:**
  - `order_id` (string, required) in url
- **Response:** Returns JSON with message or error

#### 17. **Assign Order to Delivery Person**
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



#### 18. **Order History**
- **URL:** `/orders/history/`
- **Method:** GET
- **Description:** Retrieves order history for the currently authenticated user.
- **Authorization:** Bearer Token (required)
  - Example: `'Authorization':'Bearer <your_access_token>'`
- **Response:** Returns JSON array of order objects with order id, total amount, and order date.


T Make sure to replace `<your_access_token>` placeholders with actual access tokens in your implementation. If you need further adjustments or have more questions, feel free to ask!