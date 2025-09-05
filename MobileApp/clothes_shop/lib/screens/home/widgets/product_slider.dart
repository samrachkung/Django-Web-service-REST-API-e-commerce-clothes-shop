import 'package:flutter/material.dart';
import 'package:carousel_slider/carousel_slider.dart';
import 'package:shimmer/shimmer.dart';
import 'package:clothes_shop/models/product.dart';
import 'package:clothes_shop/screens/product/product_card.dart';

class ProductSlider extends StatelessWidget {
  final List<Product> products;
  final bool isLoading;
  
  const ProductSlider({
    super.key,
    required this.products,
    this.isLoading = false,
  });
  
  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return _buildLoadingSlider();
    }
    
    if (products.isEmpty) {
      return const SizedBox(
        height: 250,
        child: Center(
          child: Text('No products available'),
        ),
      );
    }
    
    return CarouselSlider.builder(
      itemCount: products.length,
      options: CarouselOptions(
        height: 280,
        viewportFraction: 0.45,
        enlargeCenterPage: false,
        enableInfiniteScroll: products.length > 2,
        autoPlay: products.length > 2,
        autoPlayInterval: const Duration(seconds: 5),
      ),
      itemBuilder: (context, index, realIndex) {
        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8),
          child: ProductCard(product: products[index]),
        );
      },
    );
  }
  
  Widget _buildLoadingSlider() {
    return SizedBox(
      height: 280,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: 3,
        itemBuilder: (context, index) {
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Shimmer.fromColors(
              baseColor: Colors.grey[300]!,
              highlightColor: Colors.grey[100]!,
              child: Container(
                width: 180,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}