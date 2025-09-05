import 'category.dart';

class Product {
  final int id;
  final String name;
  final String description;
  final List<String> images;
  final double price;
  final double? discountPrice;
  final Category category; 
  final bool isInStock;
  final double averageRating;
  final int reviewCount;
  final List<ProductVariant> variants;
  
  Product({
    required this.id,
    required this.name,
    required this.description,
    required this.images,
    required this.price,
    this.discountPrice,
    required this.category,
    required this.isInStock,
    required this.averageRating,
    required this.reviewCount,
    required this.variants,
  });
  
  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      images: List<String>.from(json['images'] ?? []),
      price: double.tryParse(json['price'].toString()) ?? 0.0,
      discountPrice: json['discount_price'] != null 
        ? double.tryParse(json['discount_price'].toString()) 
        : null,
      category: Category.fromJson(json['category'] ?? {}),
      isInStock: json['is_in_stock'] ?? false,
      averageRating: double.tryParse((json['average_rating'] ?? 0).toString()) ?? 0.0,
      reviewCount: json['review_count'] ?? 0,
      variants: (json['variants'] as List? ?? [])
        .map((v) => ProductVariant.fromJson(v as Map<String, dynamic>))
        .toList(),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'images': images,
      'price': price,
      'discount_price': discountPrice,
      'category': category.toJson(),
      'is_in_stock': isInStock,
      'average_rating': averageRating,
      'review_count': reviewCount,
      'variants': variants.map((v) => v.toJson()).toList(),
    };
  }
  
  double get effectivePrice => discountPrice ?? price;
  double get discountPercentage {
    if (discountPrice != null && price > 0) {
      return ((price - discountPrice!) / price * 100);
    }
    return 0;
  }
  
  String get primaryImage => images.isNotEmpty ? images.first : '';
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Product && other.id == id;
  }
  
  @override
  int get hashCode => id.hashCode;
  
  @override
  String toString() {
    return 'Product(id: $id, name: $name, price: $price)';
  }
}

class ProductVariant {
  final int id;
  final Size size;
  final Color color;
  final int stockQty;
  final double? price; // Optional: variant-specific price
  
  ProductVariant({
    required this.id,
    required this.size,
    required this.color,
    required this.stockQty,
    this.price,
  });
  
  factory ProductVariant.fromJson(Map<String, dynamic> json) {
    return ProductVariant(
      id: json['id'] ?? 0,
      size: Size.fromJson(json['size'] ?? {}),
      color: Color.fromJson(json['color'] ?? {}),
      stockQty: json['stock_qty'] ?? 0,
      price: json['price'] != null ? double.tryParse(json['price'].toString()) : null,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'size': size.toJson(),
      'color': color.toJson(),
      'stock_qty': stockQty,
      'price': price,
    };
  }
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is ProductVariant && other.id == id;
  }
  
  @override
  int get hashCode => id.hashCode;
}

class Size {
  final int id;
  final String name;
  final String? code; // e.g., "S", "M", "L"
  
  Size({
    required this.id, 
    required this.name,
    this.code,
  });
  
  factory Size.fromJson(Map<String, dynamic> json) {
    return Size(
      id: json['id'] ?? 0,
      name: json['size_name'] ?? json['name'] ?? '',
      code: json['code'] ?? json['size_code'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'code': code,
    };
  }
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Size && other.id == id;
  }
  
  @override
  int get hashCode => id.hashCode;
  
  @override
  String toString() => name;
}

class Color {
  final int id;
  final String name;
  final String? hexCode;
  
  Color({
    required this.id, 
    required this.name, 
    this.hexCode,
  });
  
  factory Color.fromJson(Map<String, dynamic> json) {
    return Color(
      id: json['id'] ?? 0,
      name: json['color_name'] ?? json['name'] ?? '',
      hexCode: json['hex_code'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'hex_code': hexCode,
    };
  }
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Color && other.id == id;
  }
  
  @override
  int get hashCode => id.hashCode;
  
  @override
  String toString() => name;
}