# products/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count, Min, Max, F  # ADD F import - CRITICAL FIX
from django.db import models  # ADD THIS IMPORT - CRITICAL FIX
from .models import Category, Product, Size, Color, ProductVariant
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductCreateUpdateSerializer, SizeSerializer, ColorSerializer, 
    ProductVariantSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for product categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for products"""
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']  # Remove 'is_on_sale' as it's a property, not a field
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at', 'name']  # Remove 'discount_percentage' as it's a property
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    def get_queryset(self):
        """Custom filtering for products"""
        queryset = Product.objects.all()
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(
                Q(discount_price__gte=min_price) | 
                (Q(discount_price__isnull=True) & Q(price__gte=min_price))
            )
        
        if max_price:
            queryset = queryset.filter(
                Q(discount_price__lte=max_price) | 
                (Q(discount_price__isnull=True) & Q(price__lte=max_price))
            )
        
        # Filter by availability
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(variants__stock_qty__gt=0).distinct()
        
        # Filter by size
        size = self.request.query_params.get('size')
        if size:
            queryset = queryset.filter(
                variants__size__size_name=size,
                variants__stock_qty__gt=0
            ).distinct()
        
        # Filter by color
        color = self.request.query_params.get('color')
        if color:
            queryset = queryset.filter(
                variants__color__color_name=color,
                variants__stock_qty__gt=0
            ).distinct()
        
        # Filter by sale items
        on_sale = self.request.query_params.get('on_sale')
        if on_sale == 'true':
            queryset = queryset.filter(
                discount_price__isnull=False,
                discount_price__lt=F('price')  # Use F() expression properly
            )
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        """Get all variants for a product"""
        product = self.get_object()
        variants = product.variants.all()
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def add_variant(self, request, pk=None):
        """Add a new variant to a product"""
        product = self.get_object()
        serializer = ProductVariantSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def add_images(self, request, pk=None):
        """Add images to a product"""
        product = self.get_object()
        new_images = request.data.get('images', [])
        
        if not isinstance(new_images, list):
            return Response(
                {'error': 'Images must be a list of URLs'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add new images to existing ones
        if isinstance(product.images, list):
            product.images.extend(new_images)
        else:
            product.images = new_images
        
        product.save()
        
        return Response({
            'message': 'Images added successfully',
            'images': product.images
        })
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products (highest rated with stock)"""
        # Since reviews app might not exist yet, check if the relation exists
        products = Product.objects.filter(
            variants__stock_qty__gt=0
        ).distinct()
        
        # Only add review filtering if reviews relation exists
        try:
            products = products.annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            ).filter(
                review_count__gte=3,
                avg_rating__gte=4
            ).order_by('-avg_rating')[:10]
        except:
            # If reviews don't exist, just get products with stock
            products = products[:10]
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Get products on sale"""
        products = Product.objects.filter(
            discount_price__isnull=False,
            discount_price__lt=F('price')  # Use F() expression properly
        ).order_by('-created_at')
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        """Get new arrival products (last 30 days)"""
        from datetime import timedelta
        from django.utils import timezone
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        products = Product.objects.filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class SizeViewSet(viewsets.ModelViewSet):
    """ViewSet for sizes"""
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ColorViewSet(viewsets.ModelViewSet):
    """ViewSet for colors"""
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductVariantViewSet(viewsets.ModelViewSet):
    """ViewSet for product variants"""
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'size', 'color']
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_stock(self, request, pk=None):
        """Update stock quantity for a variant"""
        variant = self.get_object()
        new_stock = request.data.get('stock_qty')
        
        if new_stock is None:
            return Response(
                {'error': 'stock_qty is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_stock = int(new_stock)
            if new_stock < 0:
                raise ValueError
        except ValueError:
            return Response(
                {'error': 'stock_qty must be a non-negative integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        variant.stock_qty = new_stock
        variant.save()
        
        return Response({
            'message': 'Stock updated successfully',
            'variant_id': variant.id,
            'new_stock': variant.stock_qty
        })
# Add this class to your products/views.py file

class ProductImageViewSet(viewsets.ViewSet):
    """
    ViewSet for managing product images (URLs).
    This handles adding, removing, and reordering image URLs for products.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request, product_pk=None):
        """List all images for a specific product"""
        try:
            product = Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        images = product.images if isinstance(product.images, list) else []
        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'images': images,
            'count': len(images)
        })
    
    def create(self, request, product_pk=None):
        """Add new image URLs to a product"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            product = Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get image URL(s) from request
        image_url = request.data.get('image_url')
        image_urls = request.data.get('image_urls', [])
        
        if not image_url and not image_urls:
            return Response(
                {'error': 'Please provide image_url or image_urls'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize images list if needed
        if not isinstance(product.images, list):
            product.images = []
        
        # Add single or multiple URLs
        if image_url:
            product.images.append(image_url)
        if image_urls and isinstance(image_urls, list):
            product.images.extend(image_urls)
        
        product.save()
        
        return Response({
            'message': 'Images added successfully',
            'product_id': product.id,
            'images': product.images,
            'count': len(product.images)
        }, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None, product_pk=None):
        """Remove an image by index from a product"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            product = Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            index = int(pk)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid image index'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(product.images, list) or index >= len(product.images):
            return Response(
                {'error': 'Image index out of range'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        removed_image = product.images.pop(index)
        product.save()
        
        return Response({
            'message': 'Image removed successfully',
            'removed_image': removed_image,
            'remaining_images': product.images
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def reorder(self, request, product_pk=None):
        """Reorder product images"""
        try:
            product = Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        new_order = request.data.get('image_urls')
        
        if not isinstance(new_order, list):
            return Response(
                {'error': 'image_urls must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify all URLs are from the existing images
        existing_images = set(product.images) if isinstance(product.images, list) else set()
        new_images_set = set(new_order)
        
        if existing_images != new_images_set:
            return Response(
                {'error': 'New order must contain exactly the same images'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product.images = new_order
        product.save()
        
        return Response({
            'message': 'Images reordered successfully',
            'images': product.images
        })
    
    @action(detail=False, methods=['delete'], permission_classes=[IsAdminUser])
    def clear(self, request, product_pk=None):
        """Clear all images from a product"""
        try:
            product = Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        product.images = []
        product.save()
        
        return Response({
            'message': 'All images cleared successfully',
            'product_id': product.id
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def set_primary(self, request, pk=None, product_pk=None):
        """Set an image as primary (move to index 0)"""
        try:
            product = Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            index = int(pk)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid image index'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(product.images, list) or index >= len(product.images):
            return Response(
                {'error': 'Image index out of range'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Move the image to the front
        image = product.images.pop(index)
        product.images.insert(0, image)
        product.save()
        
        return Response({
            'message': 'Primary image set successfully',
            'primary_image': image,
            'images': product.images
        })        