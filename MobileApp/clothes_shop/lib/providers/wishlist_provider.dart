import 'package:flutter/material.dart';
import 'package:clothes_shop/models/product.dart';

class WishlistProvider extends ChangeNotifier {
  final List<Product> _items = [];
  
  List<Product> get items => _items;
  
  bool isInWishlist(int productId) {
    return _items.any((product) => product.id == productId);
  }
  
  void addToWishlist(Product product) {
    if (!isInWishlist(product.id)) {
      _items.add(product);
      notifyListeners();
    }
  }
  
  void removeFromWishlist(Product product) {
    _items.removeWhere((item) => item.id == product.id);
    notifyListeners();
  }
  
  void toggleWishlist(Product product) {
    if (isInWishlist(product.id)) {
      removeFromWishlist(product);
    } else {
      addToWishlist(product);
    }
  }
  
  void clearWishlist() {
    _items.clear();
    notifyListeners();
  }
}