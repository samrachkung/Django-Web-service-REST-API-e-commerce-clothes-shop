# reviews/views.py
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q, F
from django.utils import timezone

from .models import Review
from products.models import Product
from orders.models import Order, OrderItem
from .serializers import ReviewSerializer, CreateReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product reviews
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """
        Get reviews with optional filtering
        """
        queryset = Review.objects.all()
        
        # Filter by product if specified
        product_id = self.request.query_params.get('product', None)
        if product_id is not None:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user', None)
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by rating if specified
        rating = self.request.query_params.get('rating', None)
        if rating is not None:
            queryset = queryset.filter(rating=rating)
        
        # Order by created date (newest first)
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action in ['create', 'update', 'partial_update']:
            return CreateReviewSerializer
        return ReviewSerializer
    
    def perform_create(self, serializer):
        """
        Save review with current user
        """
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new review
        """
        # Check if user has purchased the product
        product_id = request.data.get('product')
        if product_id:
            has_purchased = OrderItem.objects.filter(
                order__user=request.user,
                order__status='delivered',
                product_variant__product_id=product_id
            ).exists()
            
            if not has_purchased:
                # Optional: You can still allow reviews without purchase
                pass  # Remove this pass and uncomment below to enforce purchase
                # return Response(
                #     {'error': 'You can only review products you have purchased'},
                #     status=status.HTTP_403_FORBIDDEN
                # )
        
        # Check if user already reviewed this product
        existing_review = Review.objects.filter(
            user=request.user,
            product_id=product_id
        ).first()
        
        if existing_review:
            return Response(
                {'error': 'You have already reviewed this product'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Update an existing review
        """
        review = self.get_object()
        
        # Only allow users to edit their own reviews
        if review.user != request.user:
            return Response(
                {'error': 'You can only edit your own reviews'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a review
        """
        review = self.get_object()
        
        # Only allow users to delete their own reviews (or staff)
        if review.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only delete your own reviews'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def helpful(self, request, pk=None):
        """
        Mark a review as helpful
        """
        review = self.get_object()
        
        # You could add a ManyToMany field to track who found it helpful
        # For now, just increment a counter (you'd need to add this field to the model)
        return Response({
            'message': 'Thank you for your feedback',
            'review_id': review.id
        })
    
    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """
        Get all reviews by the current user
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        reviews = Review.objects.filter(user=request.user).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        
        return Response({
            'count': reviews.count(),
            'reviews': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def product_stats(self, request):
        """
        Get review statistics for a product
        """
        product_id = request.query_params.get('product_id')
        
        if not product_id:
            return Response(
                {'error': 'product_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        reviews = Review.objects.filter(product=product)
        
        # Calculate statistics
        stats = reviews.aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('rating'),
            total_5_star=Count('id', filter=Q(rating=5)),
            total_4_star=Count('id', filter=Q(rating=4)),
            total_3_star=Count('id', filter=Q(rating=3)),
            total_2_star=Count('id', filter=Q(rating=2)),
            total_1_star=Count('id', filter=Q(rating=1)),
        )
        
        # Calculate percentages
        total = stats['total_reviews']
        if total > 0:
            stats['rating_distribution'] = {
                '5_star': {
                    'count': stats.pop('total_5_star'),
                    'percentage': round((stats['total_5_star'] / total) * 100, 1) if 'total_5_star' in stats else 0
                },
                '4_star': {
                    'count': stats.pop('total_4_star'),
                    'percentage': round((stats['total_4_star'] / total) * 100, 1) if 'total_4_star' in stats else 0
                },
                '3_star': {
                    'count': stats.pop('total_3_star'),
                    'percentage': round((stats['total_3_star'] / total) * 100, 1) if 'total_3_star' in stats else 0
                },
                '2_star': {
                    'count': stats.pop('total_2_star'),
                    'percentage': round((stats['total_2_star'] / total) * 100, 1) if 'total_2_star' in stats else 0
                },
                '1_star': {
                    'count': stats.pop('total_1_star'),
                    'percentage': round((stats['total_1_star'] / total) * 100, 1) if 'total_1_star' in stats else 0
                },
            }
        
        stats['product_id'] = product_id
        stats['product_name'] = product.name
        stats['average_rating'] = round(stats['average_rating'], 2) if stats['average_rating'] else 0
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """
        Get top-rated products based on reviews
        """
        limit = int(request.query_params.get('limit', 10))
        min_reviews = int(request.query_params.get('min_reviews', 5))
        
        # Get products with their average ratings
        products = Product.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(
            review_count__gte=min_reviews
        ).order_by('-avg_rating')[:limit]
        
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'name': product.name,
                'average_rating': round(product.avg_rating, 2) if product.avg_rating else 0,
                'review_count': product.review_count,
                'price': float(product.price),
                'discount_price': float(product.discount_price) if product.discount_price else None,
            })
        
        return Response({
            'count': len(results),
            'products': results
        })


# Additional Review-related views

class ProductReviewsView(generics.ListAPIView):
    """
    List all reviews for a specific product
    """
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Review.objects.filter(product_id=product_id).order_by('-created_at')


class UserReviewsView(generics.ListAPIView):
    """
    List all reviews by a specific user
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Review.objects.filter(user_id=user_id).order_by('-created_at')


class ReviewSummaryView(APIView):
    """
    Get a summary of reviews for the entire store
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Overall statistics
        total_reviews = Review.objects.count()
        average_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Recent reviews
        recent_reviews = Review.objects.order_by('-created_at')[:5]
        recent_serializer = ReviewSerializer(recent_reviews, many=True, context={'request': request})
        
        # Most reviewed products
        most_reviewed = Product.objects.annotate(
            review_count=Count('reviews')
        ).filter(review_count__gt=0).order_by('-review_count')[:5]
        
        most_reviewed_data = []
        for product in most_reviewed:
            most_reviewed_data.append({
                'id': product.id,
                'name': product.name,
                'review_count': product.review_count
            })
        
        # Best rated products
        best_rated = Product.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(review_count__gte=3).order_by('-avg_rating')[:5]
        
        best_rated_data = []
        for product in best_rated:
            best_rated_data.append({
                'id': product.id,
                'name': product.name,
                'average_rating': round(product.avg_rating, 2) if product.avg_rating else 0,
                'review_count': product.review_count
            })
        
        return Response({
            'summary': {
                'total_reviews': total_reviews,
                'average_rating': round(average_rating, 2),
            },
            'recent_reviews': recent_serializer.data,
            'most_reviewed_products': most_reviewed_data,
            'best_rated_products': best_rated_data
        })


class CanReviewView(APIView):
    """
    Check if a user can review a specific product
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already reviewed
        existing_review = Review.objects.filter(
            user=request.user,
            product=product
        ).exists()
        
        if existing_review:
            return Response({
                'can_review': False,
                'reason': 'Already reviewed this product'
            })
        
        # Check if purchased
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            order__status='delivered',
            product_variant__product=product
        ).exists()
        
        return Response({
            'can_review': True,
            'has_purchased': has_purchased,
            'product_id': product_id,
            'product_name': product.name
        })