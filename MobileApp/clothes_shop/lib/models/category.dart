class Category {
  final int id;
  final String name;
  final String? description;
  final String? image;
  final int productCount;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  
  Category({
    required this.id,
    required this.name,
    this.description,
    this.image,
    this.productCount = 0,
    this.createdAt,
    this.updatedAt,
  });
  
  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      description: json['description'],
      image: json['image'],
      productCount: json['product_count'] ?? 0,
      createdAt: json['created_at'] != null 
        ? DateTime.tryParse(json['created_at']) 
        : null,
      updatedAt: json['updated_at'] != null 
        ? DateTime.tryParse(json['updated_at']) 
        : null,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'image': image,
      'product_count': productCount,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Category && other.id == id;
  }
  
  @override
  int get hashCode => id.hashCode;
  
  @override
  String toString() {
    return 'Category(id: $id, name: $name)';
  }
}