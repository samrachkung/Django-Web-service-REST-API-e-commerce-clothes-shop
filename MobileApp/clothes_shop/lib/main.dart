import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:clothes_shop/app.dart';
import 'package:clothes_shop/providers/auth_provider.dart';
import 'package:clothes_shop/providers/cart_provider.dart';
import 'package:clothes_shop/providers/product_provider.dart';
import 'package:clothes_shop/providers/wishlist_provider.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ProductProvider()),
        ChangeNotifierProvider(create: (_) => CartProvider()),
        ChangeNotifierProvider(create: (_) => WishlistProvider()),
      ],
      child: const MyApp(),
    ),
  );
}