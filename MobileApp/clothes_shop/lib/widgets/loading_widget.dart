import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';

class LoadingWidget extends StatelessWidget {
  final double height;
  final double width;
  final BorderRadius? borderRadius;
  
  const LoadingWidget({
    super.key,
    this.height = 100,
    this.width = double.infinity,
    this.borderRadius,
  });
  
  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: Colors.grey[300]!,
      highlightColor: Colors.grey[100]!,
      child: Container(
        height: height,
        width: width,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: borderRadius ?? BorderRadius.circular(8),
        ),
      ),
    );
  }
}

class LoadingListWidget extends StatelessWidget {
  final int itemCount;
  final double itemHeight;
  
  const LoadingListWidget({
    super.key,
    this.itemCount = 5,
    this.itemHeight = 80,
  });
  
  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: itemCount,
      itemBuilder: (context, index) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: LoadingWidget(height: itemHeight),
        );
      },
    );
  }
}