# cart/views.py
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import F, Sum
from django.utils import timezone

from .models import Cart, CartItem, Wishlist
from products.models import ProductVariant, Product
from .serializers import (
    CartSerializer, CartItemSerializer, 
    AddToCartSerializer, UpdateCartItemSerializer, 
    WishlistSerializer
)


class CartViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing shopping cart
    """
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get or create cart for current user"""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """
        Get current user's cart
        """
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Add item to cart
        """
        cart = self.get_object()
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        variant_id = serializer.validated_data['product_variant_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return Response(
                {'error': 'Product variant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check stock availability
        if variant.stock_qty < quantity:
            return Response(
                {'error': f'Only {variant.stock_qty} items available in stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity if item already exists
            new_quantity = cart_item.quantity + quantity
            if variant.stock_qty < new_quantity:
                return Response(
                    {'error': f'Only {variant.stock_qty} items available in stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()
        
        # Return updated cart item
        return Response(
            CartItemSerializer(cart_item).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['put', 'patch'], url_path='update-item/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """
        Update cart item quantity
        """
        cart = self.get_object()
        
        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quantity = serializer.validated_data['quantity']
        
        # Check stock availability
        if cart_item.product_variant.stock_qty < quantity:
            return Response(
                {'error': f'Only {cart_item.product_variant.stock_qty} items available in stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return Response(CartItemSerializer(cart_item).data)
    
    @action(detail=False, methods=['delete'], url_path='remove-item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """
        Remove item from cart
        """
        cart = self.get_object()
        
        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
            cart_item.delete()
            return Response(
                {'message': 'Item removed from cart'},
                status=status.HTTP_204_NO_CONTENT
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """
        Clear all items from cart
        """
        cart = self.get_object()
        deleted_count = cart.items.all().delete()[0]
        return Response({
            'message': f'Cart cleared. {deleted_count} items removed',
            'items_removed': deleted_count
        })
    
    @action(detail=False, methods=['post'])
    def bulk_add(self, request):
        """
        Add multiple items to cart at once
        """
        cart = self.get_object()
        items = request.data.get('items', [])
        
        if not items:
            return Response(
                {'error': 'No items provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        added_items = []
        errors = []
        
        for item_data in items:
            try:
                variant_id = item_data.get('product_variant_id')
                quantity = item_data.get('quantity', 1)
                
                if not variant_id:
                    errors.append({'error': 'product_variant_id is required'})
                    continue
                
                variant = ProductVariant.objects.get(id=variant_id)
                
                if variant.stock_qty < quantity:
                    errors.append({
                        'variant_id': variant_id,
                        'error': f'Only {variant.stock_qty} items available'
                    })
                    continue
                
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product_variant=variant,
                    defaults={'quantity': quantity}
                )
                
                if not created:
                    new_quantity = cart_item.quantity + quantity
                    if variant.stock_qty < new_quantity:
                        errors.append({
                            'variant_id': variant_id,
                            'error': f'Only {variant.stock_qty} items available'
                        })
                        continue
                    cart_item.quantity = new_quantity
                    cart_item.save()
                
                added_items.append(CartItemSerializer(cart_item).data)
                
            except ProductVariant.DoesNotExist:
                errors.append({
                    'variant_id': variant_id,
                    'error': 'Product variant not found'
                })
            except Exception as e:
                errors.append({
                    'variant_id': variant_id if 'variant_id' in locals() else None,
                    'error': str(e)
                })
        
        return Response({
            'added_items': added_items,
            'errors': errors,
            'cart_total': float(cart.get_total()),
            'cart_items_count': cart.get_item_count()
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get cart summary with calculations
        """
        cart = self.get_object()
        
        items_data = []
        for item in cart.items.all():
            items_data.append({
                'id': item.id,
                'product_name': item.product_variant.product.name,
                'variant': f"{item.product_variant.size.size_name} - {item.product_variant.color.color_name}",
                'quantity': item.quantity,
                'unit_price': float(item.product_variant.product.effective_price),
                'subtotal': float(item.get_subtotal())
            })
        
        summary = {
            'items': items_data,
            'item_count': cart.get_item_count(),
            'subtotal': float(cart.get_total()),
            'estimated_tax': float(cart.get_total() * 0.1),  # 10% tax estimate
            'estimated_total': float(cart.get_total() * 1.1),
            'currency': 'USD'
        }
        
        return Response(summary)


class WishlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing wishlist
    """
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get wishlist items for current user"""
        return Wishlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Save wishlist item with current user"""
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Add product to wishlist
        """
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already in wishlist
        if Wishlist.objects.filter(user=request.user, product=product).exists():
            return Response(
                {'message': 'Product already in wishlist'},
                status=status.HTTP_200_OK
            )
        
        # Add to wishlist
        wishlist_item = Wishlist.objects.create(
            user=request.user,
            product=product
        )
        
        serializer = self.get_serializer(wishlist_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def move_to_cart(self, request):
        """
        Move all wishlist items to cart
        """
        wishlist_items = self.get_queryset()
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        moved_items = []
        errors = []
        
        for wishlist_item in wishlist_items:
            product = wishlist_item.product
            # Get the first available variant
            variant = product.variants.filter(stock_qty__gt=0).first()
            
            if not variant:
                errors.append({
                    'product': product.name,
                    'error': 'No variants in stock'
                })
                continue
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_variant=variant,
                defaults={'quantity': 1}
            )
            
            if not created:
                if variant.stock_qty > cart_item.quantity:
                    cart_item.quantity += 1
                    cart_item.save()
            
            moved_items.append(product.name)
            wishlist_item.delete()
        
        return Response({
            'moved_items': moved_items,
            'errors': errors,
            'message': f'{len(moved_items)} items moved to cart'
        })
    
    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk=None):
        """
        Add single wishlist item to cart
        """
        wishlist_item = self.get_object()
        product = wishlist_item.product
        
        # Get variant from request or use first available
        variant_id = request.data.get('variant_id')
        
        if variant_id:
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id,
                    product=product
                )
            except ProductVariant.DoesNotExist:
                return Response(
                    {'error': 'Invalid variant for this product'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            variant = product.variants.filter(stock_qty__gt=0).first()
            if not variant:
                return Response(
                    {'error': 'No variants in stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Add to cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_variant=variant,
            defaults={'quantity': 1}
        )
        
        if not created:
            if variant.stock_qty > cart_item.quantity:
                cart_item.quantity += 1
                cart_item.save()
            else:
                return Response(
                    {'error': 'Insufficient stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Remove from wishlist if requested
        if request.data.get('remove_from_wishlist', False):
            wishlist_item.delete()
        
        return Response({
            'message': 'Product added to cart',
            'cart_item': CartItemSerializer(cart_item).data
        })
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """
        Clear all wishlist items
        """
        deleted_count = self.get_queryset().delete()[0]
        return Response({
            'message': f'Wishlist cleared. {deleted_count} items removed'
        })


# Additional utility views

class CartQuickAddView(APIView):
    """
    Quick add to cart by product ID (adds first available variant)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get first available variant
        variant = product.variants.filter(stock_qty__gte=quantity).first()
        
        if not variant:
            return Response(
                {'error': 'No variants with sufficient stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add to cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            new_quantity = cart_item.quantity + quantity
            if variant.stock_qty < new_quantity:
                return Response(
                    {'error': f'Only {variant.stock_qty} items available'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()
        
        return Response({
            'message': 'Product added to cart',
            'cart_item': CartItemSerializer(cart_item).data
        })


class CartMergeView(APIView):
    """
    Merge guest cart with user cart after login
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        guest_cart_items = request.data.get('items', [])
        
        if not guest_cart_items:
            return Response(
                {'message': 'No items to merge'},
                status=status.HTTP_200_OK
            )
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        merged_count = 0
        errors = []
        
        for item in guest_cart_items:
            try:
                variant_id = item.get('variant_id')
                quantity = item.get('quantity', 1)
                
                variant = ProductVariant.objects.get(id=variant_id)
                
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product_variant=variant,
                    defaults={'quantity': 0}
                )
                
                new_quantity = cart_item.quantity + quantity
                
                if variant.stock_qty >= new_quantity:
                    cart_item.quantity = new_quantity
                    cart_item.save()
                    merged_count += 1
                else:
                    errors.append({
                        'variant_id': variant_id,
                        'error': 'Insufficient stock'
                    })
                    
            except ProductVariant.DoesNotExist:
                errors.append({
                    'variant_id': variant_id,
                    'error': 'Product not found'
                })
            except Exception as e:
                errors.append({
                    'variant_id': variant_id,
                    'error': str(e)
                })
        
        return Response({
            'merged_count': merged_count,
            'errors': errors,
            'cart_total': float(cart.get_total())
        })