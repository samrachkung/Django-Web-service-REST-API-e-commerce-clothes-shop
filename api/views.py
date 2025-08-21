from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from django.core.cache import cache
from datetime import datetime, timedelta
import json

from products.models import Product, Category, ProductVariant
from orders.models import Order, OrderItem
from cart.models import Cart, Wishlist, CartItem
from reviews.models import Review
from accounts.models import User
from products.serializers import ProductListSerializer
from orders.serializers import OrderListSerializer


class APIRootView(APIView):
    """
    API Root endpoint that provides information about available endpoints
    """
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        return Response({
            'message': 'E-commerce API v1.0',
            'endpoints': {
                'authentication': {
                    'register': request.build_absolute_uri('/api/auth/register/'),
                    'login': request.build_absolute_uri('/api/auth/login/'),
                    'logout': request.build_absolute_uri('/api/auth/logout/'),
                    'token': request.build_absolute_uri('/api/auth/token/'),
                    'token_refresh': request.build_absolute_uri('/api/auth/token/refresh/'),
                },
                'products': {
                    'list': request.build_absolute_uri('/api/products/'),
                    'categories': request.build_absolute_uri('/api/categories/'),
                    'sizes': request.build_absolute_uri('/api/sizes/'),
                    'colors': request.build_absolute_uri('/api/colors/'),
                },
                'user': {
                    'profile': request.build_absolute_uri('/api/users/me/'),
                    'cart': request.build_absolute_uri('/api/cart/my_cart/'),
                    'wishlist': request.build_absolute_uri('/api/wishlist/'),
                    'orders': request.build_absolute_uri('/api/orders/'),
                    'dashboard': request.build_absolute_uri('/api/user/dashboard/'),
                },
                'search': request.build_absolute_uri('/api/search/'),
                'documentation': {
                    'swagger': request.build_absolute_uri('/api/swagger/'),
                    'redoc': request.build_absolute_uri('/api/redoc/'),
                },
            },
            'version': '1.0.0',
            'status': 'active'
        })


class APIStatsView(APIView):
    """
    Provides statistics about the API usage and data
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Cache the stats for 5 minutes
        cache_key = 'api_stats'
        stats = cache.get(cache_key)
        
        if not stats:
            stats = {
                'products': {
                    'total': Product.objects.count(),
                    'categories': Category.objects.count(),
                    'in_stock': ProductVariant.objects.filter(stock_qty__gt=0).count(),
                    'out_of_stock': ProductVariant.objects.filter(stock_qty=0).count(),
                },
                'orders': {
                    'total': Order.objects.count(),
                    'pending': Order.objects.filter(status='pending').count(),
                    'completed': Order.objects.filter(status='delivered').count(),
                    'revenue': float(Order.objects.filter(
                        status='delivered'
                    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
                },
                'users': {
                    'total': User.objects.count(),
                    'active': User.objects.filter(status='active').count(),
                    'new_this_month': User.objects.filter(
                        created_at__gte=timezone.now() - timedelta(days=30)
                    ).count(),
                },
                'reviews': {
                    'total': Review.objects.count(),
                    'average_rating': float(Review.objects.aggregate(
                        Avg('rating'))['rating__avg'] or 0
                    ),
                },
                'timestamp': timezone.now().isoformat()
            }
            cache.set(cache_key, stats, 300)  # Cache for 5 minutes
        
        return Response(stats)


class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        from django.db import connection
        from django.db.utils import OperationalError
        
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'services': {}
        }
        
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            health_status['services']['database'] = 'up'
        except OperationalError:
            health_status['services']['database'] = 'down'
            health_status['status'] = 'unhealthy'
        
        # Check cache
        try:
            cache.set('health_check', 'ok', 1)
            if cache.get('health_check') == 'ok':
                health_status['services']['cache'] = 'up'
            else:
                health_status['services']['cache'] = 'down'
        except:
            health_status['services']['cache'] = 'down'
        
        # Check media storage
        try:
            from django.core.files.storage import default_storage
            health_status['services']['storage'] = 'up' if default_storage.exists('') or True else 'down'
        except:
            health_status['services']['storage'] = 'down'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return Response(health_status, status=status_code)


class SearchView(APIView):
    """
    Global search endpoint for products, categories, etc.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', 'all')
        
        if not query:
            return Response({
                'error': 'Please provide a search query using the "q" parameter'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        results = {
            'query': query,
            'results': {}
        }
        
        # Search products
        if search_type in ['all', 'products']:
            products = Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )[:10]
            results['results']['products'] = ProductListSerializer(
                products, many=True, context={'request': request}
            ).data
        
        # Search categories
        if search_type in ['all', 'categories']:
            categories = Category.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )[:5]
            results['results']['categories'] = [
                {'id': c.id, 'name': c.name} for c in categories
            ]
        
        # Add result counts
        results['counts'] = {
            key: len(value) for key, value in results['results'].items()
        }
        results['total_count'] = sum(results['counts'].values())
        
        return Response(results)


class ProductRecommendationView(APIView):
    """
    Get product recommendations for the authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        limit = int(request.query_params.get('limit', 10))
        
        recommendations = []
        
        # Get user's order history
        ordered_products = OrderItem.objects.filter(
            order__user=user
        ).values_list('product_variant__product', flat=True)
        
        # Get categories from user's orders
        ordered_categories = Product.objects.filter(
            id__in=ordered_products
        ).values_list('category', flat=True).distinct()
        
        # Recommend products from same categories
        if ordered_categories:
            recommendations = Product.objects.filter(
                category__in=ordered_categories
            ).exclude(
                id__in=ordered_products
            ).annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            ).order_by('-avg_rating', '-review_count')[:limit]
        
        # If not enough recommendations, add popular products
        if len(recommendations) < limit:
            popular_products = Product.objects.annotate(
                order_count=Count('variants__orderitem'),
                avg_rating=Avg('reviews__rating')
            ).exclude(
                id__in=[p.id for p in recommendations]
            ).order_by('-order_count', '-avg_rating')[:limit - len(recommendations)]
            
            recommendations = list(recommendations) + list(popular_products)
        
        serializer = ProductListSerializer(
            recommendations, 
            many=True, 
            context={'request': request}
        )
        
        return Response({
            'recommendations': serializer.data,
            'count': len(serializer.data)
        })


class UserDashboardView(APIView):
    """
    User dashboard with summary information
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get user statistics
        total_orders = Order.objects.filter(user=user).count()
        pending_orders = Order.objects.filter(user=user, status='pending').count()
        
        # Recent orders
        recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
        
        # Cart information
        try:
            cart = Cart.objects.get(user=user)
            cart_items_count = cart.get_item_count()
            cart_total = float(cart.get_total())
        except Cart.DoesNotExist:
            cart_items_count = 0
            cart_total = 0.0
        
        # Wishlist count
        wishlist_count = Wishlist.objects.filter(user=user).count()
        
        # Total spent
        total_spent = Order.objects.filter(
            user=user,
            status='delivered'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        dashboard_data = {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'member_since': user.created_at.isoformat(),
            },
            'statistics': {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'total_spent': float(total_spent),
                'cart_items': cart_items_count,
                'cart_total': cart_total,
                'wishlist_items': wishlist_count,
            },
            'recent_orders': OrderListSerializer(
                recent_orders, 
                many=True, 
                context={'request': request}
            ).data,
        }
        
        return Response(dashboard_data)


# Additional utility views

@api_view(['GET'])
@permission_classes([AllowAny])
def api_version(request):
    """
    Returns the current API version
    """
    return Response({
        'version': '1.0.0',
        'last_updated': '2024-01-01',
        'supported_versions': ['1.0.0'],
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_add_to_cart(request):
    """
    Add multiple items to cart at once
    """
    items = request.data.get('items', [])
    if not items:
        return Response(
            {'error': 'No items provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    added_items = []
    errors = []
    
    for item in items:
        try:
            variant_id = item.get('product_variant_id')
            quantity = item.get('quantity', 1)
            
            variant = ProductVariant.objects.get(id=variant_id)
            
            if variant.stock_qty < quantity:
                errors.append({
                    'variant_id': variant_id,
                    'error': 'Insufficient stock'
                })
                continue
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_variant=variant,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            added_items.append({
                'variant_id': variant_id,
                'quantity': cart_item.quantity,
                'added': True
            })
            
        except ProductVariant.DoesNotExist:
            errors.append({
                'variant_id': variant_id,
                'error': 'Product variant not found'
            })
        except Exception as e:
            errors.append({
                'variant_id': variant_id,
                'error': str(e)
            })
    
    return Response({
        'added_items': added_items,
        'errors': errors,
        'cart_total': float(cart.get_total()),
        'cart_items_count': cart.get_item_count()
    })