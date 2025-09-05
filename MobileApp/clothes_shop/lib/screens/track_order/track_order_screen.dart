import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class TrackOrderScreen extends StatefulWidget {
  const TrackOrderScreen({super.key});

  @override
  State<TrackOrderScreen> createState() => _TrackOrderScreenState();
}

class _TrackOrderScreenState extends State<TrackOrderScreen> {
  final _orderIdController = TextEditingController();
  bool _isTracking = false;
  Map<String, dynamic>? _orderStatus;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Track Order'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Search Section
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.1),
                    spreadRadius: 1,
                    blurRadius: 5,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Enter Order ID',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Enter your order ID to track your package',
                    style: TextStyle(color: Colors.grey),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _orderIdController,
                    decoration: InputDecoration(
                      hintText: 'e.g., ORD123456789',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      prefixIcon: const Icon(Icons.search),
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _isTracking ? null : _trackOrder,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: _isTracking
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Text('Track Order'),
                    ),
                  ),
                ],
              ),
            ),
            
            // Order Status
            if (_orderStatus != null) ...[
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.withOpacity(0.1),
                      spreadRadius: 1,
                      blurRadius: 5,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Order Status',
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            color: _getStatusColor(_orderStatus!['status']),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            _orderStatus!['status'].toUpperCase(),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    
                    // Tracking Timeline
                    _buildTrackingTimeline(),
                    
                    const Divider(height: 32),
                    
                    // Order Details
                    Text(
                      'Order Details',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _buildDetailRow('Order ID', _orderStatus!['orderId']),
                    _buildDetailRow('Order Date', _orderStatus!['orderDate']),
                    _buildDetailRow('Estimated Delivery', _orderStatus!['estimatedDelivery']),
                    if (_orderStatus!['trackingNumber'] != null)
                      _buildDetailRow('Tracking Number', _orderStatus!['trackingNumber']),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  Widget _buildTrackingTimeline() {
    final steps = [
      {'title': 'Order Placed', 'date': 'Jan 15, 2024', 'completed': true},
      {'title': 'Processing', 'date': 'Jan 15, 2024', 'completed': true},
      {'title': 'Shipped', 'date': 'Jan 16, 2024', 'completed': true},
      {'title': 'Out for Delivery', 'date': 'Jan 18, 2024', 'completed': false},
      {'title': 'Delivered', 'date': 'Expected Jan 18', 'completed': false},
    ];
    
    return Column(
      children: steps.asMap().entries.map((entry) {
        final index = entry.key;
        final step = entry.value;
        final isLast = index == steps.length - 1;
        
        return Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Column(
              children: [
                Container(
                  width: 24,
                  height: 24,
                  decoration: BoxDecoration(
                    color: step['completed'] as bool
                        ? Theme.of(context).primaryColor
                        : Colors.grey[300],
                    shape: BoxShape.circle,
                  ),
                  child: step['completed'] as bool
                      ? const Icon(
                          Icons.check,
                          size: 16,
                          color: Colors.white,
                        )
                      : null,
                ),
                if (!isLast)
                  Container(
                    width: 2,
                    height: 50,
                    color: step['completed'] as bool
                        ? Theme.of(context).primaryColor
                        : Colors.grey[300],
                  ),
              ],
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.only(bottom: 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      step['title'] as String,
                      style: TextStyle(
                        fontWeight: FontWeight.w500,
                        color: step['completed'] as bool
                            ? Colors.black
                            : Colors.grey,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      step['date'] as String,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      }).toList(),
    );
  }
  
  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(color: Colors.grey[600]),
          ),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }
  
  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'delivered':
        return Colors.green;
      case 'shipped':
      case 'out for delivery':
        return Colors.blue;
      case 'processing':
        return Colors.orange;
      case 'canceled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
  
  Future<void> _trackOrder() async {
    if (_orderIdController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter order ID')),
      );
      return;
    }
    
    setState(() {
      _isTracking = true;
    });
    
    // Simulate API call
    await Future.delayed(const Duration(seconds: 2));
    
    setState(() {
      _isTracking = false;
      _orderStatus = {
        'orderId': _orderIdController.text,
        'status': 'shipped',
        'orderDate': DateFormat('MMM dd, yyyy').format(
          DateTime.now().subtract(const Duration(days: 3)),
        ),
        'estimatedDelivery': DateFormat('MMM dd, yyyy').format(
          DateTime.now().add(const Duration(days: 2)),
        ),
        'trackingNumber': 'TRK${DateTime.now().millisecondsSinceEpoch}',
      };
    });
  }
  
  @override
  void dispose() {
    _orderIdController.dispose();
    super.dispose();
  }
}