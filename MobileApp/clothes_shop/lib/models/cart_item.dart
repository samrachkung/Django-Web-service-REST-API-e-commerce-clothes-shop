// models/cart_item.dart
import 'package:clothes_shop/models/product.dart';

class CartItem {
  final Product product;
  final ProductVariant variant;
  int quantity;
  final DateTime? addedAt;
  
  CartItem({
    required this.product,
    required this.variant,
    required this.quantity,
    this.addedAt,
  });
  
  // Calculate total price for this cart item
  double get totalPrice => product.effectivePrice * quantity;
  
  // Get formatted variant info
  String get variantInfo => '${variant.size.name} / ${variant.color.name}';
  
  // Check if item is in stock
  bool get isInStock => variant.stockQty >= quantity;
  
  // Get available stock
  int get availableStock => variant.stockQty;
  
  // Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'product_id': product.id,
      'variant_id': variant.id,
      'quantity': quantity,
      'added_at': addedAt?.toIso8601String(),
    };
  }
  
  // Create from JSON (for local storage or API response)
  factory CartItem.fromJson(Map<String, dynamic> json, Product product, ProductVariant variant) {
    return CartItem(
      product: product,
      variant: variant,
      quantity: json['quantity'] ?? 1,
      addedAt: json['added_at'] != null ? DateTime.parse(json['added_at']) : null,
    );
  }
  
  // Create a copy with updated values
  CartItem copyWith({
    Product? product,
    ProductVariant? variant,
    int? quantity,
    DateTime? addedAt,
  }) {
    return CartItem(
      product: product ?? this.product,
      variant: variant ?? this.variant,
      quantity: quantity ?? this.quantity,
      addedAt: addedAt ?? this.addedAt,
    );
  }
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    
    return other is CartItem &&
        other.product.id == product.id &&
        other.variant.id == variant.id;
  }
  
  @override
  int get hashCode => product.id.hashCode ^ variant.id.hashCode;
  
  @override
  String toString() {
    return 'CartItem(product: ${product.name}, variant: $variantInfo, quantity: $quantity)';
  }
}

// Optional: Cart model to hold all cart items
class Cart {
  final List<CartItem> items;
  final DateTime createdAt;
  final DateTime updatedAt;
  
  Cart({
    required this.items,
    required this.createdAt,
    required this.updatedAt,
  });
  
  // Calculate cart subtotal
  double get subtotal {
    return items.fold(0, (sum, item) => sum + item.totalPrice);
  }
  
  // Calculate tax (10% by default)
  double get tax {
    return subtotal * 0.1;
  }
  
  // Calculate total
  double get total {
    return subtotal + tax;
  }
  
  // Get total item count
  int get itemCount {
    return items.fold(0, (sum, item) => sum + item.quantity);
  }
  
  // Get unique item count
  int get uniqueItemCount {
    return items.length;
  }
  
  // Check if cart is empty
  bool get isEmpty {
    return items.isEmpty;
  }
  
  // Check if cart has items
  bool get hasItems {
    return items.isNotEmpty;
  }
  
  // Find item by product and variant
  CartItem? findItem(int productId, int variantId) {
    try {
      return items.firstWhere(
        (item) => item.product.id == productId && item.variant.id == variantId,
      );
    } catch (e) {
      return null;
    }
  }
  
  // Add item to cart
  void addItem(CartItem item) {
    final existingItem = findItem(item.product.id, item.variant.id);
    if (existingItem != null) {
      existingItem.quantity += item.quantity;
    } else {
      items.add(item);
    }
  }
  
  // Remove item from cart
  void removeItem(CartItem item) {
    items.removeWhere(
      (cartItem) => cartItem.product.id == item.product.id && 
                    cartItem.variant.id == item.variant.id,
    );
  }
  
  // Update item quantity
  void updateItemQuantity(CartItem item, int newQuantity) {
    if (newQuantity <= 0) {
      removeItem(item);
    } else {
      final index = items.indexOf(item);
      if (index != -1) {
        items[index].quantity = newQuantity;
      }
    }
  }
  
  // Clear all items
  void clear() {
    items.clear();
  }
  
  // Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'items': items.map((item) => item.toJson()).toList(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
  
  // Create from JSON
  factory Cart.fromJson(Map<String, dynamic> json, List<Product> products, List<ProductVariant> variants) {
    final itemsList = <CartItem>[];
    
    if (json['items'] != null) {
      for (var itemJson in json['items']) {
        final product = products.firstWhere(
          (p) => p.id == itemJson['product_id'],
        );
        final variant = variants.firstWhere(
          (v) => v.id == itemJson['variant_id'],
        );
        itemsList.add(CartItem.fromJson(itemJson, product, variant));
      }
    }
    
    return Cart(
      items: itemsList,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
}