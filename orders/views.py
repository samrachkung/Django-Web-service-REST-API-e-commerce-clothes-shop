from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Order, OrderItem, Payment, Shipping, Discount, OrderDiscount
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, CreateOrderSerializer,
    PaymentSerializer, ShippingSerializer, DiscountSerializer
)
from cart.models import Cart

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return CreateOrderSerializer
        return OrderDetailSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                return Response(
                    {'error': 'Cart is empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Cart.DoesNotExist:
            return Response(
                {'error': 'No cart found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create order
        order = Order.objects.create(user=request.user)
        
        # Create order items from cart
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_variant=cart_item.product_variant,
                quantity=cart_item.quantity,
                price_at_time=cart_item.product_variant.product.effective_price
            )
        
        # Apply discounts
        discount_codes = serializer.validated_data.get('discount_codes', [])
        for code in discount_codes:
            try:
                discount = Discount.objects.get(code=code)
                if discount.is_valid():
                    OrderDiscount.objects.create(order=order, discount=discount)
                    discount.times_used += 1
                    discount.save()
            except Discount.DoesNotExist:
                pass
        
        # Calculate total
        order.calculate_total()
        
        # Create shipping info
        Shipping.objects.create(
            order=order,
            shipping_address=serializer.validated_data['shipping_address'],
            shipping_method=serializer.validated_data['shipping_method']
        )
        
        # Create payment record
        Payment.objects.create(
            order=order,
            method=serializer.validated_data['payment_method'],
            amount=order.total_amount
        )
        
        # Clear cart
        cart.items.all().delete()
        
        return Response(
            OrderDetailSerializer(order).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in ['pending', 'paid']:
            order.status = 'canceled'
            order.save()
            return Response({'status': 'Order canceled'})
        return Response(
            {'error': 'Cannot cancel this order'},
            status=status.HTTP_400_BAD_REQUEST
        )

class DiscountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Discount.objects.filter(is_active=True)
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        code = request.data.get('code')
        try:
            discount = Discount.objects.get(code=code)
            if discount.is_valid():
                return Response({
                    'valid': True,
                    'discount': DiscountSerializer(discount).data
                })
        except Discount.DoesNotExist:
            pass
        
        return Response({'valid': False})

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        payment = self.get_object()
        
        if payment.status == 'paid':
            return Response(
                {'error': 'Payment already confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # In production, integrate with payment gateway here
        payment.status = 'paid'
        payment.paid_at = timezone.now()
        payment.transaction_id = request.data.get('transaction_id', 'TEST_TRANSACTION')
        payment.save()
        
        # Update order status
        order = payment.order
        order.status = 'paid'
        order.save()
        
        return Response(
            {'message': 'Payment confirmed successfully'},
            status=status.HTTP_200_OK
        )

class ShippingViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Shipping.objects.filter(order__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_tracking(self, request, pk=None):
        shipping = self.get_object()
        tracking_number = request.data.get('tracking_number')
        
        if not tracking_number:
            return Response(
                {'error': 'Tracking number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        shipping.tracking_number = tracking_number
        shipping.shipping_status = 'shipped'
        shipping.shipped_at = timezone.now()
        shipping.save()
        
        return Response(
            {'message': 'Tracking number updated'},
            status=status.HTTP_200_OK
        )    