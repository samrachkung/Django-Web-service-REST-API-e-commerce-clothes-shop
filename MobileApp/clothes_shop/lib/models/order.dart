import 'package:clothes_shop/models/product.dart';
import 'package:clothes_shop/models/user.dart';

class Order {
  final int id;
  final User user;
  final DateTime orderDate;
  final String status;
  final double totalAmount;
  final List<OrderItem> items;
  final Payment? payment;
  final Shipping? shipping;
  final DateTime createdAt;
  final DateTime updatedAt;
  
  Order({
    required this.id,
    required this.user,
    required this.orderDate,
    required this.status,
    required this.totalAmount,
    required this.items,
    this.payment,
    this.shipping,
    required this.createdAt,
    required this.updatedAt,
  });
  
  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'],
      user: User.fromJson(json['user']),
      orderDate: DateTime.parse(json['order_date']),
      status: json['status'],
      totalAmount: double.parse(json['total_amount'].toString()),
      items: (json['items'] as List? ?? [])
          .map((item) => OrderItem.fromJson(item))
          .toList(),
      payment: json['payment'] != null ? Payment.fromJson(json['payment']) : null,
      shipping: json['shipping'] != null ? Shipping.fromJson(json['shipping']) : null,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
}

class OrderItem {
  final int id;
  final ProductVariant productVariant;
  final int quantity;
  final double priceAtTime;
  
  OrderItem({
    required this.id,
    required this.productVariant,
    required this.quantity,
    required this.priceAtTime,
  });
  
  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      id: json['id'],
      productVariant: ProductVariant.fromJson(json['product_variant']),
      quantity: json['quantity'],
      priceAtTime: double.parse(json['price_at_time'].toString()),
    );
  }
  
  double get total => priceAtTime * quantity;
}

class Payment {
  final int id;
  final String method;
  final String status;
  final String? transactionId;
  final double amount;
  final DateTime? paidAt;
  
  Payment({
    required this.id,
    required this.method,
    required this.status,
    this.transactionId,
    required this.amount,
    this.paidAt,
  });
  
  factory Payment.fromJson(Map<String, dynamic> json) {
    return Payment(
      id: json['id'],
      method: json['method'],
      status: json['status'],
      transactionId: json['transaction_id'],
      amount: double.parse(json['amount'].toString()),
      paidAt: json['paid_at'] != null ? DateTime.parse(json['paid_at']) : null,
    );
  }
}

class Shipping {
  final int id;
  final String shippingAddress;
  final String shippingMethod;
  final String shippingStatus;
  final String? trackingNumber;
  final DateTime? shippedAt;
  final DateTime? deliveredAt;
  
  Shipping({
    required this.id,
    required this.shippingAddress,
    required this.shippingMethod,
    required this.shippingStatus,
    this.trackingNumber,
    this.shippedAt,
    this.deliveredAt,
  });
  
  factory Shipping.fromJson(Map<String, dynamic> json) {
    return Shipping(
      id: json['id'],
      shippingAddress: json['shipping_address'],
      shippingMethod: json['shipping_method'],
      shippingStatus: json['shipping_status'],
      trackingNumber: json['tracking_number'],
      shippedAt: json['shipped_at'] != null ? DateTime.parse(json['shipped_at']) : null,
      deliveredAt: json['delivered_at'] != null ? DateTime.parse(json['delivered_at']) : null,
    );
  }
}