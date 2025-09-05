import 'package:clothes_shop/services/api_service.dart';
import 'package:clothes_shop/models/product.dart';
import 'package:clothes_shop/models/category.dart';

class ProductService {
  final ApiService _apiService = ApiService();
  
  Future<List<Product>> getProducts({
    String? category,
    double? minPrice,
    double? maxPrice,
    String? size,
    String? color,
    String? sortBy,
    int? page,
  }) async {
    try {
      final params = <String, dynamic>{};
      
      if (category != null) params['category'] = category;
      if (minPrice != null) params['min_price'] = minPrice;
      if (maxPrice != null) params['max_price'] = maxPrice;
      if (size != null) params['size'] = size;
      if (color != null) params['color'] = color;
      if (sortBy != null) params['ordering'] = sortBy;
      if (page != null) params['page'] = page;
      
      final response = await _apiService.get('/products/', params: params);
      
      final products = (response.data['results'] as List? ?? [])
          .map((json) => Product.fromJson(json as Map<String, dynamic>))
          .toList();
      
      return products;
    } catch (e) {
      throw Exception('Failed to load products: ${e.toString()}');
    }
  }
  
  Future<Product> getProductById(int id) async {
    try {
      final response = await _apiService.get('/products/$id/');
      return Product.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw Exception('Failed to load product: ${e.toString()}');
    }
  }
  
  Future<List<Product>> getFeaturedProducts() async {
    try {
      final response = await _apiService.get('/products/featured/');
      final data = response.data;
      
      List<dynamic> productList;
      if (data is Map<String, dynamic> && data.containsKey('results')) {
        productList = data['results'] as List? ?? [];
      } else if (data is List) {
        productList = data;
      } else {
        productList = [];
      }
      
      return productList
          .map((json) => Product.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      throw Exception('Failed to load featured products: ${e.toString()}');
    }
  }
  
  Future<List<Product>> getDiscountProducts() async {
    try {
      final response = await _apiService.get('/products/on_sale/');
      final data = response.data;
      
      List<dynamic> productList;
      if (data is Map<String, dynamic> && data.containsKey('results')) {
        productList = data['results'] as List? ?? [];
      } else if (data is List) {
        productList = data;
      } else {
        productList = [];
      }
      
      return productList
          .map((json) => Product.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      throw Exception('Failed to load discount products: ${e.toString()}');
    }
  }
  
  Future<List<Product>> getNewArrivals() async {
    try {
      final response = await _apiService.get('/products/new_arrivals/');
      final data = response.data;
      
      List<dynamic> productList;
      if (data is Map<String, dynamic> && data.containsKey('results')) {
        productList = data['results'] as List? ?? [];
      } else if (data is List) {
        productList = data;
      } else {
        productList = [];
      }
      
      return productList
          .map((json) => Product.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      throw Exception('Failed to load new arrivals: ${e.toString()}');
    }
  }
  
  Future<List<Product>> getBestSellers() async {
    try {
      final response = await _apiService.get('/products/bestsellers/');
      final data = response.data;
      
      List<dynamic> productList;
      if (data is Map<String, dynamic> && data.containsKey('results')) {
        productList = data['results'] as List? ?? [];
      } else if (data is List) {
        productList = data;
      } else {
        // Fallback to featured products if bestsellers endpoint doesn't exist
        return await getFeaturedProducts();
      }
      
      return productList
          .map((json) => Product.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      // Fallback to featured products if bestsellers endpoint doesn't exist
      return await getFeaturedProducts();
    }
  }
  
  Future<List<Product>> getTrendingProducts() async {
    try {
      final response = await _apiService.get('/products/trending/');
      final data = response.data;
      
      List<dynamic> productList;
      if (data is Map<String, dynamic> && data.containsKey('results')) {
        productList = data['results'] as List? ?? [];
      } else if (data is List) {
        productList = data;
      } else {
        // Fallback to discount products if trending endpoint doesn't exist
        return await getDiscountProducts();
      }
      
      return productList
          .map((json) => Product.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      // Fallback to discount products if trending endpoint doesn't exist
      return await getDiscountProducts();
    }
  }
  
  Future<List<Category>> getCategories() async {
    try {
      final response = await _apiService.get('/categories/');
      final data = response.data;
      
      List<dynamic> categoryList;
      if (data is Map<String, dynamic> && data.containsKey('results')) {
        categoryList = data['results'] as List? ?? [];
      } else if (data is List) {
        categoryList = data;
      } else {
        categoryList = [];
      }
      
      return categoryList
          .map((json) => Category.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      throw Exception('Failed to load categories: ${e.toString()}');
    }
  }
  
  Future<List<Map<String, dynamic>>> getSizes() async {
    try {
      final response = await _apiService.get('/sizes/');
      final data = response.data;
      
      if (data is Map<String, dynamic> && data.containsKey('results')) {
        return List<Map<String, dynamic>>.from(data['results'] ?? []);
      } else if (data is List) {
        return List<Map<String, dynamic>>.from(data);
      } else {
        return [];
      }
    } catch (e) {
      throw Exception('Failed to load sizes: ${e.toString()}');
    }
  }
  
  Future<List<Map<String, dynamic>>> getColors() async {
    try {
      final response = await _apiService.get('/colors/');
      final data = response.data;
      
      if (data is Map<String, dynamic> && data.containsKey('results')) {
        return List<Map<String, dynamic>>.from(data['results'] ?? []);
      } else if (data is List) {
        return List<Map<String, dynamic>>.from(data);
      } else {
        return [];
      }
    } catch (e) {
      throw Exception('Failed to load colors: ${e.toString()}');
    }
  }
}