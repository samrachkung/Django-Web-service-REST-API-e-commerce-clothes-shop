import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:carousel_slider/carousel_slider.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:clothes_shop/providers/product_provider.dart';
import 'package:clothes_shop/screens/home/widgets/product_slider.dart';
// import 'package:clothes_shop/screens/home/widgets/discount_banner.dart';
import 'package:clothes_shop/screens/home/widgets/product_grid.dart';
import 'package:clothes_shop/widgets/custom_app_bar.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    _loadData();
  }
  
  Future<void> _loadData() async {
    final provider = context.read<ProductProvider>();
    await Future.wait([
      provider.loadFeaturedProducts(),
      provider.loadDiscountProducts(),
      provider.loadNewArrivals(),
      provider.loadBestSellers(),
      provider.loadTrendingProducts(),
    ]);
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomAppBar(title: 'Clothes Shop'),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Hero Slider
              _buildHeroSlider(),
              
              // Discount Products
              _buildSection(
                title: 'Special Discounts',
                child: Consumer<ProductProvider>(
                  builder: (context, provider, _) {
                    return ProductSlider(
                      products: provider.discountProducts,
                      isLoading: provider.isLoading,
                    );
                  },
                ),
              ),
              
              // New Arrivals
              _buildSection(
                title: 'New Arrivals',
                child: Consumer<ProductProvider>(
                  builder: (context, provider, _) {
                    return ProductGrid(
                      products: provider.newArrivals,
                      isLoading: provider.isLoading,
                    );
                  },
                ),
              ),
              
              // Bestsellers
              _buildSection(
                title: 'Bestsellers',
                child: Consumer<ProductProvider>(
                  builder: (context, provider, _) {
                    return ProductSlider(
                      products: provider.bestSellers,
                      isLoading: provider.isLoading,
                    );
                  },
                ),
              ),
              
              // Trending Products
              _buildSection(
                title: 'Trending Now',
                child: Consumer<ProductProvider>(
                  builder: (context, provider, _) {
                    return ProductGrid(
                      products: provider.trendingProducts,
                      isLoading: provider.isLoading,
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildHeroSlider() {
    final banners = [
      'https://example.com/banner1.jpg',
      'https://example.com/banner2.jpg',
      'https://example.com/banner3.jpg',
    ];
    
    return CarouselSlider(
      options: CarouselOptions(
        height: 200,
        autoPlay: true,
        enlargeCenterPage: true,
        viewportFraction: 0.9,
      ),
      items: banners.map((url) {
        return Builder(
          builder: (BuildContext context) {
            return Container(
              width: MediaQuery.of(context).size.width,
              margin: const EdgeInsets.symmetric(horizontal: 5.0),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                color: Colors.grey[300],
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: CachedNetworkImage(
                  imageUrl: url,
                  fit: BoxFit.cover,
                  placeholder: (context, url) => const Center(
                    child: CircularProgressIndicator(),
                  ),
                  errorWidget: (context, url, error) => const Icon(Icons.error),
                ),
              ),
            );
          },
        );
      }).toList(),
    );
  }
  
  Widget _buildSection({required String title, required Widget child}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                TextButton(
                  onPressed: () {
                    // Navigate to see all
                  },
                  child: const Text('See All'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          child,
        ],
      ),
    );
  }
}