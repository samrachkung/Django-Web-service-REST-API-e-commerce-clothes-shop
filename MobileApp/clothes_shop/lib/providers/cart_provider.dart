import 'package:flutter/material.dart';
import 'package:clothes_shop/models/product.dart';
import 'package:clothes_shop/models/cart_item.dart';
import 'dart:collection';

class CartProvider extends ChangeNotifier {
  final List<CartItem> _items = [];

  // Expose an unmodifiable view
  UnmodifiableListView<CartItem> get items => UnmodifiableListView(_items);

  // Check if cart is empty
  bool get isEmpty => _items.isEmpty;

  // Check if cart has items
  bool get isNotEmpty => _items.isNotEmpty;

  // Calculate subtotal - FIXED: use product.effectivePrice instead of variant.price
  double get subtotal {
    return _items.fold(0.0, (sum, item) => sum + (item.quantity * item.product.effectivePrice));
  }

  // Calculate tax (10% tax rate)
  double get tax {
    return subtotal * 0.1;
  }

  // Calculate shipping (free shipping over $50, otherwise $5)
  double get shipping {
    return subtotal >= 50.0 ? 0.0 : 5.0;
  }

  // Calculate total
  double get total {
    return subtotal + tax + shipping;
  }

  // Get total number of items in cart
  int get itemCount {
    return _items.fold(0, (sum, item) => sum + item.quantity);
  }

  // Get number of unique products in cart
  int get uniqueItemCount => _items.length;

  // Check if a specific product variant is in cart
  bool isInCart(Product product, ProductVariant variant) {
    return _items.any((item) => 
      item.product.id == product.id && item.variant.id == variant.id
    );
  }

  // Get quantity of a specific product variant in cart
  int getQuantity(Product product, ProductVariant variant) {
    try {
      final item = _items.firstWhere(
        (item) => item.product.id == product.id && item.variant.id == variant.id,
      );
      return item.quantity;
    } catch (e) {
      return 0;
    }
  }

  // Add item to cart
  void addToCart(Product product, ProductVariant variant, int quantity) {
    if (quantity <= 0) return;

    // Check if variant has enough stock
    if (quantity > variant.stockQty) {
      throw Exception('Not enough stock available. Only ${variant.stockQty} items left.');
    }

    final existingIndex = _items.indexWhere(
      (item) => item.product.id == product.id && item.variant.id == variant.id,
    );

    if (existingIndex != -1) {
      final newQuantity = _items[existingIndex].quantity + quantity;
      
      // Check if total quantity would exceed stock
      if (newQuantity > variant.stockQty) {
        throw Exception('Cannot add more items. Only ${variant.stockQty} items available.');
      }

      // Update existing item
      _items[existingIndex] = _items[existingIndex].copyWith(
        quantity: newQuantity,
      );
    } else {
      // Add new item
      _items.add(CartItem(
        product: product,
        variant: variant,
        quantity: quantity,
        addedAt: DateTime.now(),
      ));
    }

    notifyListeners();
  }

  // Remove item from cart completely
  void removeFromCart(CartItem item) {
    _items.removeWhere((cartItem) =>
      cartItem.product.id == item.product.id &&
      cartItem.variant.id == item.variant.id
    );
    notifyListeners();
  }

  // Remove item by product and variant
  void removeItemByProductVariant(Product product, ProductVariant variant) {
    _items.removeWhere((cartItem) =>
      cartItem.product.id == product.id &&
      cartItem.variant.id == variant.id
    );
    notifyListeners();
  }

  // Update quantity of an item
  void updateQuantity(CartItem item, int newQuantity) {
    if (newQuantity < 0) return;

    final index = _items.indexWhere((cartItem) =>
      cartItem.product.id == item.product.id &&
      cartItem.variant.id == item.variant.id
    );

    if (index != -1) {
      if (newQuantity == 0) {
        // Remove item if quantity is 0
        _items.removeAt(index);
      } else {
        // Check if new quantity exceeds stock
        if (newQuantity > item.variant.stockQty) {
          throw Exception('Cannot update quantity. Only ${item.variant.stockQty} items available.');
        }

        // Update item quantity
        _items[index] = _items[index].copyWith(quantity: newQuantity);
      }
      notifyListeners();
    }
  }

  // Increment item quantity
  void incrementQuantity(CartItem item) {
    final newQuantity = item.quantity + 1;
    if (newQuantity <= item.variant.stockQty) {
      updateQuantity(item, newQuantity);
    } else {
      throw Exception('Cannot add more items. Maximum stock reached.');
    }
  }

  // Decrement item quantity
  void decrementQuantity(CartItem item) {
    final newQuantity = item.quantity - 1;
    updateQuantity(item, newQuantity);
  }

  // Clear entire cart
  void clearCart() {
    _items.clear();
    notifyListeners();
  }

  // Get cart summary for checkout
  Map<String, dynamic> getCartSummary() {
    return {
      'items': _items.map((item) => item.toJson()).toList(), // FIXED: use toJson() instead of toApiJson()
      'subtotal': subtotal,
      'tax': tax,
      'shipping': shipping,
      'total': total,
      'item_count': itemCount,
      'unique_item_count': uniqueItemCount,
    };
  }

  // Validate cart items (check stock availability)
  List<String> validateCart() {
    List<String> errors = [];
    
    for (var item in _items) {
      if (!item.isInStock) {
        errors.add('${item.product.name} (${item.variantInfo}) is out of stock'); // FIXED: use available properties
      } else if (item.quantity > item.variant.stockQty) { // FIXED: use direct comparison instead of isQuantityAvailable
        errors.add('${item.product.name} (${item.variantInfo}) - only ${item.variant.stockQty} items available, but ${item.quantity} requested');
      }
    }
    
    return errors;
  }

  // Remove out of stock items
  void removeOutOfStockItems() {
    _items.removeWhere((item) => !item.isInStock);
    notifyListeners();
  }

  // Update quantities to available stock
  void adjustToAvailableStock() {
    bool hasChanges = false;
    
    for (int i = 0; i < _items.length; i++) {
      final item = _items[i];
      if (item.quantity > item.variant.stockQty && item.isInStock) { // FIXED: use direct comparison
        _items[i] = item.copyWith(quantity: item.variant.stockQty);
        hasChanges = true;
      }
    }
    
    if (hasChanges) {
      notifyListeners();
    }
  }

  // Save cart to JSON (for persistence)
  Map<String, dynamic> toJson() {
    return {
      'items': _items.map((item) => item.toJson()).toList(),
      'last_updated': DateTime.now().toIso8601String(),
    };
  }

  // REMOVED: fromJson method as it references CartItem.fromJson incorrectly
  // The CartItem.fromJson method requires Product and ProductVariant objects
  // which aren't available in this context. This method should be implemented
  // at a higher level where these objects are accessible.

  // Load cart from JSON with proper dependencies
  void loadFromJson(Map<String, dynamic> json, List<Product> products, List<ProductVariant> variants) {
    _items.clear();
    if (json['items'] != null) {
      for (var itemJson in json['items']) {
        try {
          // Find the product and variant
          final product = products.firstWhere(
            (p) => p.id == itemJson['product_id'],
          );
          final variant = variants.firstWhere(
            (v) => v.id == itemJson['variant_id'],
          );
          _items.add(CartItem.fromJson(itemJson, product, variant));
        } catch (e) {
          // Skip invalid items
          debugPrint('Error loading cart item: $e');
        }
      }
    }
    notifyListeners();
  }
}