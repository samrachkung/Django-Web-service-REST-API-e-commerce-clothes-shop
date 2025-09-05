import 'package:clothes_shop/services/api_service.dart';
import 'package:clothes_shop/models/order.dart';

class OrderService {
  final ApiService _apiService = ApiService();
  
  Future<List<Order>> getOrders() async {
    try {
      final response = await _apiService.get('/orders/');
      final orders = (response.data['results'] as List? ?? [])
          .map((json) => Order.fromJson(json))
          .toList();
      return orders;
    } catch (e) {
      throw Exception('Failed to load orders: ${e.toString()}');
    }
  }
  
  Future<Order> getOrderById(int id) async {
    try {
      final response = await _apiService.get('/orders/$id/');
      return Order.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to load order: ${e.toString()}');
    }
  }
  
  Future<Order> createOrder({
    required String shippingAddress,
    required String shippingMethod,
    required String paymentMethod,
    List<String>? discountCodes,
  }) async {
    try {
      final response = await _apiService.post('/orders/', data: {
        'shipping_address': shippingAddress,
        'shipping_method': shippingMethod,
        'payment_method': paymentMethod,
        'discount_codes': discountCodes ?? [],
      });
      return Order.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to create order: ${e.toString()}');
    }
  }
  
  Future<void> cancelOrder(int orderId) async {
    try {
      await _apiService.post('/orders/$orderId/cancel/');
    } catch (e) {
      throw Exception('Failed to cancel order: ${e.toString()}');
    }
  }
  
  Future<Map<String, dynamic>> trackOrder(String orderId) async {
    try {
      final response = await _apiService.get('/orders/track/', params: {
        'order_id': orderId,
      });
      return response.data;
    } catch (e) {
      throw Exception('Failed to track order: ${e.toString()}');
    }
  }
  
  Future<Map<String, dynamic>> validateDiscount(String code) async {
    try {
      final response = await _apiService.post('/discounts/validate/', data: {
        'code': code,
      });
      return response.data;
    } catch (e) {
      throw Exception('Invalid discount code');
    }
  }
}