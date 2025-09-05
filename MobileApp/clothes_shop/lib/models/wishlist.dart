import 'package:clothes_shop/models/product.dart';
import 'package:clothes_shop/models/user.dart';

class WishlistItem {
  final int id;
  final User user;
  final Product product;
  final DateTime addedAt;
  
  WishlistItem({
    required this.id,
    required this.user,
    required this.product,
    required this.addedAt,
  });
  
  factory WishlistItem.fromJson(Map<String, dynamic> json) {
    return WishlistItem(
      id: json['id'],
      user: User.fromJson(json['user']),
      product: Product.fromJson(json['product']),
      addedAt: DateTime.parse(json['added_at']),
    );
  }
}