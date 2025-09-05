import 'package:flutter/material.dart';
import 'package:clothes_shop/models/product.dart';
import 'package:clothes_shop/models/category.dart';
import 'package:clothes_shop/services/product_service.dart';

class ProductProvider extends ChangeNotifier {
  final ProductService _productService = ProductService();
  
  List<Product> _products = [];
  List<Product> _featuredProducts = [];
  List<Product> _discountProducts = [];
  List<Product> _newArrivals = [];
  List<Product> _bestSellers = [];
  List<Product> _trendingProducts = [];
  List<Category> _categories = [];
  
  bool _isLoading = false;
  String? _error;
  
  // Getters
  List<Product> get products => _products;
  List<Product> get featuredProducts => _featuredProducts;
  List<Product> get discountProducts => _discountProducts;
  List<Product> get newArrivals => _newArrivals;
  List<Product> get bestSellers => _bestSellers;
  List<Product> get trendingProducts => _trendingProducts;
  List<Category> get categories => _categories;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  Future<void> loadProducts({
    String? category,
    double? minPrice,
    double? maxPrice,
    String? size,
    String? color,
    String? sortBy,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      _products = await _productService.getProducts(
        category: category,
        minPrice: minPrice,
        maxPrice: maxPrice,
        size: size,
        color: color,
        sortBy: sortBy,
      );
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<void> loadFeaturedProducts() async {
    _setLoading(true);
    try {
      _featuredProducts = await _productService.getFeaturedProducts();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _setLoading(false);
    }
  }
  
  Future<void> loadDiscountProducts() async {
    _setLoading(true);
    try {
      _discountProducts = await _productService.getDiscountProducts();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _setLoading(false);
    }
  }
  
  Future<void> loadNewArrivals() async {
    _setLoading(true);
    try {
      _newArrivals = await _productService.getNewArrivals();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _setLoading(false);
    }
  }
  
  Future<void> loadBestSellers() async {
    _setLoading(true);
    try {
      // You can implement a dedicated API endpoint for bestsellers
      _bestSellers = await _productService.getBestSellers();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _setLoading(false);
    }
  }
  
  Future<void> loadTrendingProducts() async {
    _setLoading(true);
    try {
      // You can implement a dedicated API endpoint for trending products
      _trendingProducts = await _productService.getTrendingProducts();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _setLoading(false);
    }
  }
  
  Future<void> loadCategories() async {
    _setLoading(true);
    try {
      _categories = await _productService.getCategories();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _setLoading(false);
    }
  }
  
  // Load all initial data
  Future<void> loadInitialData() async {
    await Future.wait([
      loadProducts(),
      loadFeaturedProducts(),
      loadDiscountProducts(),
      loadNewArrivals(),
      loadBestSellers(),
      loadTrendingProducts(),
      loadCategories(),
    ]);
  }
  
  Product? getProductById(int id) {
    try {
      return _products.firstWhere((product) => product.id == id);
    } catch (e) {
      return null;
    }
  }
  
  List<Product> getProductsByCategory(int categoryId) {
    return _products.where((product) => product.category.id == categoryId).toList();
  }
  
  List<Product> searchProducts(String query) {
    if (query.isEmpty) return _products;
    
    final lowercaseQuery = query.toLowerCase();
    return _products.where((product) {
      return product.name.toLowerCase().contains(lowercaseQuery) ||
             product.description.toLowerCase().contains(lowercaseQuery) ||
             product.category.name.toLowerCase().contains(lowercaseQuery);
    }).toList();
  }
  
  void clearError() {
    _error = null;
    notifyListeners();
  }
  
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
  
  // Refresh all data
  Future<void> refresh() async {
    await loadInitialData();
  }
}