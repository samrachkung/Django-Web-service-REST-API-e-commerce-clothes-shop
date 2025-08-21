# orders/serializers.py
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import (
    Order, OrderItem, Payment, Shipping, 
    Discount, OrderDiscount
)
from products.models import ProductVariant
from accounts.models import User


# ============================================
# Product Variant Nested Serializer
# ============================================

class ProductVariantDetailSerializer(serializers.ModelSerializer):
    """Detailed product variant info for order items"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price', 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    size_name = serializers.CharField(source='size.size_name', read_only=True)
    color_name = serializers.CharField(source='color.color_name', read_only=True)
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product_name', 'product_price', 
            'size_name', 'color_name', 'stock_qty', 'product_image'
        ]
    
    def get_product_image(self, obj):
        """Get primary product image"""
        primary_image = obj.product.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request and primary_image.image:
                return request.build_absolute_uri(primary_image.image.url)
        return None


# ============================================
# Order Item Serializers
# ============================================

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    product_variant = ProductVariantDetailSerializer(read_only=True)
    product_variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source='product_variant',
        write_only=True
    )
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_variant', 'product_variant_id', 
            'quantity', 'price_at_time', 'total'
        ]
        read_only_fields = ['price_at_time']
    
    def get_total(self, obj):
        """Calculate total for this item"""
        return str(obj.get_total())
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class OrderItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating order items"""
    product_variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source='product_variant'
    )
    
    class Meta:
        model = OrderItem
        fields = ['product_variant_id', 'quantity']
    
    def validate(self, attrs):
        """Validate stock availability"""
        product_variant = attrs['product_variant']
        quantity = attrs['quantity']
        
        if product_variant.stock_qty < quantity:
            raise serializers.ValidationError({
                'quantity': f'Only {product_variant.stock_qty} items available in stock'
            })
        
        return attrs


# ============================================
# Payment Serializers
# ============================================

class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment information"""
    order_id = serializers.PrimaryKeyRelatedField(
        source='order',
        read_only=True
    )
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order_id', 'method', 'status', 
            'transaction_id', 'amount', 'paid_at'
        ]
        read_only_fields = ['transaction_id', 'paid_at', 'amount']
    
    def validate_method(self, value):
        """Validate payment method"""
        valid_methods = [choice[0] for choice in Payment.METHOD_CHOICES]
        if value not in valid_methods:
            raise serializers.ValidationError(
                f"Invalid payment method. Choose from: {', '.join(valid_methods)}"
            )
        return value


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment"""
    class Meta:
        model = Payment
        fields = ['method']
    
    def validate_method(self, value):
        """Validate payment method"""
        valid_methods = [choice[0] for choice in Payment.METHOD_CHOICES]
        if value not in valid_methods:
            raise serializers.ValidationError(
                f"Invalid payment method. Choose from: {', '.join(valid_methods)}"
            )
        return value


# ============================================
# Shipping Serializers
# ============================================

class ShippingSerializer(serializers.ModelSerializer):
    """Serializer for shipping information"""
    order_id = serializers.PrimaryKeyRelatedField(
        source='order',
        read_only=True
    )
    estimated_delivery = serializers.SerializerMethodField()
    
    class Meta:
        model = Shipping
        fields = [
            'id', 'order_id', 'shipping_address', 'shipping_method',
            'shipping_status', 'tracking_number', 'shipped_at', 
            'delivered_at', 'estimated_delivery'
        ]
        read_only_fields = ['tracking_number', 'shipped_at', 'delivered_at']
    
    def get_estimated_delivery(self, obj):
        """Calculate estimated delivery date"""
        if obj.delivered_at:
            return obj.delivered_at
        elif obj.shipped_at:
            # Estimate 3-5 days from shipping
            from datetime import timedelta
            return obj.shipped_at + timedelta(days=5)
        return None


class ShippingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating shipping info"""
    class Meta:
        model = Shipping
        fields = ['shipping_address', 'shipping_method']
    
    def validate_shipping_address(self, value):
        """Validate shipping address"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Please provide a complete shipping address"
            )
        return value.strip()


class ShippingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating shipping info"""
    class Meta:
        model = Shipping
        fields = [
            'shipping_address', 'shipping_method', 
            'shipping_status', 'tracking_number'
        ]


# ============================================
# Discount Serializers
# ============================================

class DiscountSerializer(serializers.ModelSerializer):
    """Serializer for discount codes"""
    is_valid = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Discount
        fields = [
            'id', 'code', 'description', 'discount_type', 
            'amount', 'valid_from', 'valid_to', 'usage_limit', 
            'times_used', 'is_active', 'is_valid', 'discount_amount'
        ]
        read_only_fields = ['times_used']
    
    def get_is_valid(self, obj):
        """Check if discount is currently valid"""
        return obj.is_valid()
    
    def get_discount_amount(self, obj):
        """Get formatted discount amount"""
        if obj.discount_type == 'percent':
            return f"{obj.amount}%"
        return f"${obj.amount}"


class OrderDiscountSerializer(serializers.ModelSerializer):
    """Serializer for applied discounts on orders"""
    discount = DiscountSerializer(read_only=True)
    discount_code = serializers.CharField(write_only=True, required=False)
    saved_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderDiscount
        fields = ['id', 'discount', 'discount_code', 'saved_amount']
    
    def get_saved_amount(self, obj):
        """Calculate amount saved by this discount"""
        if obj.order and obj.discount:
            subtotal = sum(item.get_total() for item in obj.order.items.all())
            return str(obj.discount.get_discount_amount(subtotal))
        return "0.00"


# ============================================
# Order Serializers
# ============================================

class OrderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for order list view"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user_email', 'user_name', 'order_date', 
            'status', 'status_display', 'total_amount', 
            'item_count', 'created_at'
        ]
        read_only_fields = ['order_date', 'total_amount', 'created_at']
    
    def to_representation(self, instance):
        """Add item count to representation"""
        data = super().to_representation(instance)
        data['item_count'] = instance.items.count()
        return data


class OrderDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single order view"""
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    shipping = ShippingSerializer(read_only=True)
    discounts = OrderDiscountSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    subtotal = serializers.SerializerMethodField()
    discount_total = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'user_email', 'user_name', 'order_date', 
            'status', 'status_display', 'total_amount', 'subtotal',
            'discount_total', 'items', 'payment', 'shipping', 
            'discounts', 'can_cancel', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'order_date', 'total_amount', 'created_at', 'updated_at'
        ]
    
    def get_subtotal(self, obj):
        """Calculate subtotal before discounts"""
        return str(sum(item.get_total() for item in obj.items.all()))
    
    def get_discount_total(self, obj):
        """Calculate total discount amount"""
        subtotal = sum(item.get_total() for item in obj.items.all())
        discount_amount = sum(
            discount.discount.get_discount_amount(subtotal) 
            for discount in obj.discounts.all()
            if discount.discount.is_valid()
        )
        return str(discount_amount)
    
    def get_can_cancel(self, obj):
        """Check if order can be cancelled"""
        return obj.status in ['pending', 'paid']


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating a new order"""
    # Order items (optional - will use cart if not provided)
    items = OrderItemCreateSerializer(many=True, required=False)
    
    # Shipping information
    shipping_address = serializers.CharField(required=True)
    shipping_method = serializers.CharField(required=True)
    
    # Payment information
    payment_method = serializers.CharField(required=True)
    
    # Discount codes (optional)
    discount_codes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    
    # Additional options
    use_cart = serializers.BooleanField(default=True)
    clear_cart_after = serializers.BooleanField(default=True)
    
    def validate_payment_method(self, value):
        """Validate payment method"""
        valid_methods = [choice[0] for choice in Payment.METHOD_CHOICES]
        if value not in valid_methods:
            raise serializers.ValidationError(
                f"Invalid payment method. Choose from: {', '.join(valid_methods)}"
            )
        return value
    
    def validate_discount_codes(self, value):
        """Validate discount codes"""
        if not value:
            return []
        
        valid_codes = []
        for code in value:
            try:
                discount = Discount.objects.get(code=code)
                if not discount.is_valid():
                    raise serializers.ValidationError(
                        f"Discount code '{code}' is not valid or has expired"
                    )
                valid_codes.append(code)
            except Discount.DoesNotExist:
                raise serializers.ValidationError(
                    f"Discount code '{code}' does not exist"
                )
        
        return valid_codes
    
    def validate(self, attrs):
        """Validate the entire order"""
        user = self.context['request'].user
        use_cart = attrs.get('use_cart', True)
        items = attrs.get('items', [])
        
        if use_cart:
            # Check if cart has items
            from cart.models import Cart
            try:
                cart = Cart.objects.get(user=user)
                if not cart.items.exists():
                    raise serializers.ValidationError(
                        "Your cart is empty. Add items before creating an order."
                    )
            except Cart.DoesNotExist:
                raise serializers.ValidationError(
                    "No cart found. Please add items to cart first."
                )
        elif not items:
            raise serializers.ValidationError(
                "Please provide items or use cart to create an order."
            )
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """Create order with all related objects"""
        user = self.context['request'].user
        use_cart = validated_data.get('use_cart', True)
        clear_cart = validated_data.get('clear_cart_after', True)
        
        # Create order
        order = Order.objects.create(
            user=user,
            status='pending'
        )
        
        # Add items to order
        if use_cart:
            from cart.models import Cart
            cart = Cart.objects.get(user=user)
            
            for cart_item in cart.items.all():
                # Check stock again
                if cart_item.product_variant.stock_qty < cart_item.quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {cart_item.product_variant}"
                    )
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product_variant=cart_item.product_variant,
                    quantity=cart_item.quantity,
                    price_at_time=cart_item.product_variant.product.effective_price
                )
                
                # Update stock
                cart_item.product_variant.stock_qty -= cart_item.quantity
                cart_item.product_variant.save()
            
            # Clear cart if requested
            if clear_cart:
                cart.items.all().delete()
        else:
            # Create from provided items
            for item_data in validated_data.get('items', []):
                variant = item_data['product_variant']
                quantity = item_data['quantity']
                
                # Check stock
                if variant.stock_qty < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {variant}"
                    )
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product_variant=variant,
                    quantity=quantity,
                    price_at_time=variant.product.effective_price
                )
                
                # Update stock
                variant.stock_qty -= quantity
                variant.save()
        
        # Apply discount codes
        for code in validated_data.get('discount_codes', []):
            discount = Discount.objects.get(code=code)
            OrderDiscount.objects.create(order=order, discount=discount)
            discount.times_used += 1
            discount.save()
        
        # Calculate total
        order.calculate_total()
        
        # Create shipping info
        Shipping.objects.create(
            order=order,
            shipping_address=validated_data['shipping_address'],
            shipping_method=validated_data['shipping_method']
        )
        
        # Create payment record
        Payment.objects.create(
            order=order,
            method=validated_data['payment_method'],
            amount=order.total_amount,
            status='pending'
        )
        
        return order
    
    def to_representation(self, instance):
        """Return created order details"""
        return OrderDetailSerializer(instance, context=self.context).data


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status"""
    class Meta:
        model = Order
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status transition"""
        if self.instance:
            current_status = self.instance.status
            
            # Define valid transitions
            valid_transitions = {
                'pending': ['paid', 'canceled'],
                'paid': ['shipped', 'canceled'],
                'shipped': ['delivered', 'canceled'],
                'delivered': [],
                'canceled': []
            }
            
            if value not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from '{current_status}' to '{value}'"
                )
        
        return value