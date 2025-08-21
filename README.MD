# Django Ecommerce Clothes Shop ST20 API

A comprehensive REST API for an e-commerce platform built with Django and Django REST Framework. This API provides complete functionality for managing products, orders, shopping carts, user accounts, and product reviews.

## 🚀 Features

- **User Authentication & Authorization**: JWT-based authentication with role-based access control
- **Product Management**: Full CRUD operations for products with categories, variants (size/color), and multiple images
- **Shopping Cart**: Session-based and user-based cart functionality
- **Order Processing**: Complete order lifecycle management with status tracking
- **Review System**: Product ratings and reviews with verified purchase validation
- **Admin Dashboard**: Django admin interface for managing all resources
- **API Documentation**: Interactive Swagger/OpenAPI documentation
- **Search & Filtering**: Advanced product search with multiple filter options
- **Pagination**: Efficient data loading with customizable pagination

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- PostgreSQL (optional, SQLite by default)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/samrachkung/Django-Web-service-REST-API-e-commerce-clothes-shop.git
cd ecommerce_shop
```

### 2. Set Up Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
DATABASE_URL=postgresql://user:password@localhost/dbname

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-email-password

# Media Files
MEDIA_URL=/media/
MEDIA_ROOT=media/

# Security (for production)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

**Default Test Credentials:**
- Username: `admin`
- Email: `admin@gmail.com`
- Password: `Admin12345678`

### 7. Load Sample Data (Optional)

```bash
python manage.py loaddata fixtures/sample_data.json
```

### 8. Run Development Server

```bash
python manage.py runserver
```

## 🌐 API Endpoints

### Base URLs
- **API Root**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/swagger/

### Main Endpoints

#### Authentication
```
POST   /api/auth/register/         # User registration
POST   /api/auth/login/            # User login
POST   /api/auth/logout/           # User logout
POST   /api/auth/refresh/          # Refresh JWT token
GET    /api/auth/user/             # Get current user
PUT    /api/auth/user/             # Update user profile
POST   /api/auth/change-password/  # Change password
POST   /api/auth/reset-password/   # Password reset request
```

#### Products
```
GET    /api/products/              # List all products
POST   /api/products/              # Create product (admin)
GET    /api/products/{id}/         # Get product details
PUT    /api/products/{id}/         # Update product (admin)
DELETE /api/products/{id}/         # Delete product (admin)
GET    /api/products/featured/     # Get featured products
GET    /api/products/on-sale/      # Get products on sale
GET    /api/products/new-arrivals/ # Get new arrivals

# Product Variants
GET    /api/products/{id}/variants/           # Get product variants
POST   /api/products/{id}/add_variant/        # Add variant (admin)

# Product Images
GET    /api/products/{id}/images/             # List product images
POST   /api/products/{id}/images/             # Add images (admin)
DELETE /api/products/{id}/images/{index}/     # Remove image (admin)
POST   /api/products/{id}/images/reorder/     # Reorder images (admin)
```

#### Categories
```
GET    /api/categories/            # List all categories
POST   /api/categories/            # Create category (admin)
GET    /api/categories/{id}/       # Get category details
PUT    /api/categories/{id}/       # Update category (admin)
DELETE /api/categories/{id}/       # Delete category (admin)
```

#### Cart
```
GET    /api/cart/                  # Get cart items
POST   /api/cart/add/              # Add item to cart
PUT    /api/cart/update/{id}/      # Update cart item
DELETE /api/cart/remove/{id}/      # Remove from cart
DELETE /api/cart/clear/            # Clear cart
```

#### Orders
```
GET    /api/orders/                # List user orders
POST   /api/orders/                # Create new order
GET    /api/orders/{id}/           # Get order details
PUT    /api/orders/{id}/cancel/    # Cancel order
GET    /api/orders/{id}/invoice/   # Download invoice
```

#### Reviews
```
GET    /api/reviews/               # List all reviews
POST   /api/products/{id}/reviews/ # Add product review
GET    /api/reviews/{id}/          # Get review details
PUT    /api/reviews/{id}/          # Update review
DELETE /api/reviews/{id}/          # Delete review
```

### Query Parameters

#### Product Filtering
```
GET /api/products/?category=1&min_price=10&max_price=100&size=M&color=Red&on_sale=true&in_stock=true
```

#### Pagination
```
GET /api/products/?page=1&page_size=20
```

#### Search
```
GET /api/products/?search=shirt
```

#### Ordering
```
GET /api/products/?ordering=-created_at  # Newest first
GET /api/products/?ordering=price        # Price: low to high
GET /api/products/?ordering=-price       # Price: high to low
```

## 📁 Project Structure

```
ecommerce_shop/
│
├── venv/                      # Virtual environment
├── ecommerce_config/          # Project configuration
│   ├── __init__.py
│   ├── settings.py           # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── asgi.py              # ASGI configuration
│   └── wsgi.py              # WSGI configuration
│
├── api/                       # API app
│   ├── __init__.py
│   ├── apps.py
│   ├── urls.py              # API URL routing
│   ├── views.py             # API views and endpoints
│   ├── serializers.py       # API-specific serializers
│   ├── permissions.py       # Custom permissions
│   ├── pagination.py        # Custom pagination classes
│   └── tests.py            # API tests
│
├── accounts/                  # User management app
│   ├── migrations/          # Database migrations
│   ├── __init__.py
│   ├── admin.py            # Admin interface configuration
│   ├── apps.py             # App configuration
│   ├── models.py           # User models
│   ├── serializers.py      # User serializers
│   ├── views.py            # User views
│   └── urls.py             # User URLs
│
├── products/                  # Product management app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py           # Product, Category, Variant models
│   ├── serializers.py      # Product serializers
│   ├── views.py            # Product views
│   └── urls.py
│
├── orders/                    # Order management app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py           # Order, OrderItem models
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── cart/                      # Shopping cart app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py           # Cart, CartItem models
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── reviews/                   # Product reviews app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py           # Review, Rating models
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── media/                     # User uploaded files
│   └── products/             # Product images
│
├── static/                    # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/                 # HTML templates (if needed)
│   └── email/               # Email templates
│
├── fixtures/                  # Sample data
│   └── sample_data.json
│
├── tests/                     # Test suite
│   ├── test_products.py
│   ├── test_orders.py
│   ├── test_cart.py
│   └── test_auth.py
│
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore file
└── README.md                 # This file
```

## 🔧 Configuration

### Database Models

#### Product Model
- **Fields**: name, description, images (JSON), price, discount_price, category
- **Relations**: Has many variants, reviews
- **Properties**: effective_price, discount_percentage, is_on_sale

#### Product Variant Model
- **Fields**: product, size, color, stock_qty
- **Unique Constraint**: (product, size, color)

#### Order Model
- **Fields**: user, status, total_amount, shipping_address, created_at
- **Status Options**: pending, processing, shipped, delivered, cancelled

#### Review Model
- **Fields**: product, user, rating (1-5), comment, created_at
- **Constraint**: One review per user per product

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test products
python manage.py test orders

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## 📊 API Examples

### Register New User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "samrachkung",
    "email": "samrach@gmail.com.com",
    "password": "samrach@123!",
    "first_name": "Kung",
    "last_name": "Samrach"
  }'
```

### Add Product to Cart
```bash
curl -X POST http://localhost:8000/api/cart/add/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token" \
  -d '{
    "product_id": 1,
    "variant_id": 3,
    "quantity": 2
  }'
```

### Create Order
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token" \
  -d '{
    "shipping_address": {
      "street": "123 Main St",
      "city": "New York",
      "state": "NY",
      "zip_code": "10001",
      "country": "USA"
    },
    "payment_method": "credit_card"
  }'
```

## 🚀 Deployment

### Production Settings

1. Update `.env` for production:
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
SECRET_KEY=your-production-secret-key
```

2. Collect static files:
```bash
python manage.py collectstatic
```

3. Use production server (Gunicorn):
```bash
pip install gunicorn
gunicorn ecommerce_config.wsgi:application
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "ecommerce_config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/ecommerce
    depends_on:
      - db
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=ecommerce
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Kung Samrach** - Initial work - [YourGitHub](https://github.com/samrachkung)

## 🙏 Acknowledgments

- Django Documentation
- Django REST Framework
- All contributors who helped with this project

## 📞 Support

For support, email samrach088@gmail.com or open an issue in the GitHub repository.

## 🔒 Security

comming soon

---

**Note**: This is a development project. For production use, ensure proper security measures, environment configuration, and testing are in place.