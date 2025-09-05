import 'package:clothes_shop/services/api_service.dart';

class CartService {
  final ApiService _apiService = ApiService();
  
  Future<Map<String, dynamic>> getCart() async {
    try {
      final response = await _apiService.get('/cart/my_cart/');
      return response.data;
    } catch (e) {
      throw Exception('Failed to load cart: ${e.toString()}');
    }
  }
  
  Future<Map<String, dynamic>> addToCart({
    required int productVariantId,
    required int quantity,
  }) async {
    try {
      final response = await _apiService.post('/cart/add_item/', data: {
        'product_variant_id': productVariantId,
        'quantity': quantity,
      });
      return response.data;
    } catch (e) {
      throw Exception('Failed to add to cart: ${e.toString()}');
    }
  }
  
  Future<Map<String, dynamic>> updateCartItem({
    required int itemId,
    required int quantity,
  }) async {
    try {
      final response = await _apiService.put('/cart/update-item/$itemId/', data: {
        'quantity': quantity,
      });
      return response.data;
    } catch (e) {
      throw Exception('Failed to update cart item: ${e.toString()}');
    }
  }
  
  Future<void> removeFromCart(int itemId) async {
    try {
      await _apiService.delete('/cart/remove-item/$itemId/');
    } catch (e) {
      throw Exception('Failed to remove from cart: ${e.toString()}');
    }
  }
  
  Future<void> clearCart() async {
    try {
      await _apiService.post('/cart/clear/');
    } catch (e) {
      throw Exception('Failed to clear cart: ${e.toString()}');
    }
  }
}