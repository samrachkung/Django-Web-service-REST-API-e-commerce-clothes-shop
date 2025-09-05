import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_staggered_grid_view/flutter_staggered_grid_view.dart';
import 'package:clothes_shop/providers/product_provider.dart';
import 'package:clothes_shop/screens/product/product_card.dart';
// import 'package:clothes_shop/models/product.dart';

class CatalogScreen extends StatefulWidget {
  const CatalogScreen({super.key});

  @override
  State<CatalogScreen> createState() => _CatalogScreenState();
}

class _CatalogScreenState extends State<CatalogScreen> {
  String? _selectedCategory;
  RangeValues _priceRange = const RangeValues(0, 500);
  String? _selectedSize;
  String? _selectedColor;
  String _sortBy = 'newest';
  bool _showFilters = false;

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  Future<void> _loadProducts() async {
    await context.read<ProductProvider>().loadProducts(
      category: _selectedCategory,
      minPrice: _priceRange.start,
      maxPrice: _priceRange.end,
      size: _selectedSize,
      color: _selectedColor,
      sortBy: _sortBy,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Catalog'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () {
              setState(() {
                _showFilters = !_showFilters;
              });
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Filters
          if (_showFilters) _buildFilters(),
          
          // Products Grid
          Expanded(
            child: Consumer<ProductProvider>(
              builder: (context, provider, _) {
                if (provider.isLoading) {
                  return const Center(child: CircularProgressIndicator());
                }
                
                if (provider.products.isEmpty) {
                  return const Center(
                    child: Text('No products found'),
                  );
                }
                
                return RefreshIndicator(
                  onRefresh: _loadProducts,
                  child: MasonryGridView.count(
                    crossAxisCount: 2,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    padding: const EdgeInsets.all(16),
                    itemCount: provider.products.length,
                    itemBuilder: (context, index) {
                      return ProductCard(product: provider.products[index]);
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilters() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 3,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Column(
        children: [
          // Category Filter
          _buildFilterChips(
            title: 'Category',
            options: ['T-Shirts', 'Shirts', 'Pants', 'Dresses', 'Jackets'],
            selected: _selectedCategory,
            onSelected: (value) {
              setState(() {
                _selectedCategory = value;
              });
              _loadProducts();
            },
          ),
          
          // Price Range Filter
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Price Range: \${_priceRange.start.toInt()} - \${_priceRange.end.toInt()}',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                RangeSlider(
                  values: _priceRange,
                  min: 0,
                  max: 500,
                  divisions: 50,
                  labels: const RangeLabels(
                    '\${_priceRange.start.toInt()}',
                    '\${_priceRange.end.toInt()}',
                  ),
                  onChanged: (values) {
                    setState(() {
                      _priceRange = values;
                    });
                  },
                  onChangeEnd: (values) {
                    _loadProducts();
                  },
                ),
              ],
            ),
          ),
          
          // Sort Options
          _buildSortOptions(),
        ],
      ),
    );
  }

  Widget _buildFilterChips({
    required String title,
    required List<String> options,
    String? selected,
    required Function(String?) onSelected,
  }) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleSmall,
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: options.map((option) {
              final isSelected = selected == option;
              return FilterChip(
                label: Text(option),
                selected: isSelected,
                onSelected: (selected) {
                  onSelected(selected ? option : null);
                },
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildSortOptions() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Text(
            'Sort by:',
            style: Theme.of(context).textTheme.titleSmall,
          ),
          const SizedBox(width: 16),
          Expanded(
            child: DropdownButton<String>(
              value: _sortBy,
              isExpanded: true,
              items: const [
                DropdownMenuItem(value: 'newest', child: Text('Newest')),
                DropdownMenuItem(value: 'price_low', child: Text('Price: Low to High')),
                DropdownMenuItem(value: 'price_high', child: Text('Price: High to Low')),
                DropdownMenuItem(value: 'popular', child: Text('Most Popular')),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    _sortBy = value;
                  });
                  _loadProducts();
                }
              },
            ),
          ),
        ],
      ),
    );
  }
}