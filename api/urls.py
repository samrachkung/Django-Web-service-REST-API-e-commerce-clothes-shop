from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Import viewsets from all apps
from accounts.views import (
    RegisterView, 
    LoginView, 
    LogoutView,
    UserViewSet, 
    RoleViewSet, 
    AdminLogViewSet,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangePasswordView,
)
from products.views import (
    CategoryViewSet, 
    ProductViewSet, 
    SizeViewSet,
    ColorViewSet, 
    ProductVariantViewSet, 
    ProductImageViewSet,
)
from orders.views import (
    OrderViewSet, 
    DiscountViewSet,
    PaymentViewSet,
    ShippingViewSet,
)
from cart.views import (
    CartViewSet, 
    WishlistViewSet,
)
from reviews.views import ReviewViewSet

# Import custom API views
from .views import (
    APIRootView,
    APIStatsView,
    HealthCheckView,
    SearchView,
    ProductRecommendationView,
    UserDashboardView,
)

# Create router
router = DefaultRouter()

# Register viewsets with descriptive names
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'admin-logs', AdminLogViewSet, basename='adminlog')

# Product related endpoints
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'sizes', SizeViewSet, basename='size')
router.register(r'colors', ColorViewSet, basename='color')
router.register(r'product-variants', ProductVariantViewSet, basename='productvariant')
router.register(r'product-images', ProductImageViewSet, basename='productimage')

# Order related endpoints
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'discounts', DiscountViewSet, basename='discount')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'shipping', ShippingViewSet, basename='shipping')

# Cart and Wishlist
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

# Reviews
router.register(r'reviews', ReviewViewSet, basename='review')

app_name = 'api'

urlpatterns = [
    # API Root and utilities
    path('', APIRootView.as_view(), name='api-root'),
    path('stats/', APIStatsView.as_view(), name='api-stats'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('search/', SearchView.as_view(), name='search'),
    
    # Authentication endpoints
    path('auth/', include([
        path('register/', RegisterView.as_view(), name='register'),
        path('login/', LoginView.as_view(), name='login'),
        path('logout/', LogoutView.as_view(), name='logout'),
        path('change-password/', ChangePasswordView.as_view(), name='change-password'),
        path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
        path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
        
        # JWT endpoints
        path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    ])),
    
    # User specific endpoints
    path('user/', include([
        path('dashboard/', UserDashboardView.as_view(), name='user-dashboard'),
        path('recommendations/', ProductRecommendationView.as_view(), name='product-recommendations'),
    ])),
    
    # Include router URLs
    path('', include(router.urls)),
    
    # Version 2 API (for future use)
    path('v2/', include('api.v2_urls')),
]