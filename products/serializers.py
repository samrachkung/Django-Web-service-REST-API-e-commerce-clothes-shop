# products/serializers.py
from rest_framework import serializers
from django.db import models  # ADD THIS IMPORT - CRITICAL FIX
from .models import Category, Product, Size, Color, ProductVariant
from django.db.models import Avg, Count

class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    product_count = serializers.IntegerField(
        source='products.count', 
        read_only=True
    )
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 
            'product_count', 'created_at', 'updated_at'
        ]


class SizeSerializer(serializers.ModelSerializer):
    """Size serializer"""
    class Meta:
        model = Size
        fields = ['id', 'size_name']


class ColorSerializer(serializers.ModelSerializer):
    """Color serializer"""
    class Meta:
        model = Color
        fields = ['id', 'color_name', 'hex_code']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Product variant serializer"""
    size = SizeSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    size_id = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(), 
        source='size', 
        write_only=True
    )
    color_id = serializers.PrimaryKeyRelatedField(
        queryset=Color.objects.all(), 
        source='color', 
        write_only=True
    )
    variant_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'size', 'color', 'size_id', 'color_id', 
            'stock_qty', 'is_in_stock', 'variant_name'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified product serializer for list views"""
    category = CategorySerializer(read_only=True)
    primary_image = serializers.CharField(read_only=True)
    effective_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    discount_percentage = serializers.FloatField(read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'primary_image', 'price', 
            'discount_price', 'effective_price', 'discount_percentage',
            'is_on_sale', 'category', 'is_in_stock',
            'average_rating', 'review_count', 'created_at'
        ]
    
    def get_average_rating(self, obj):
        """Get average rating for the product"""
        # Check if reviews relation exists
        if hasattr(obj, 'reviews'):
            result = obj.reviews.aggregate(Avg('rating'))
            return round(result['rating__avg'], 2) if result['rating__avg'] else 0
        return 0
    
    def get_review_count(self, obj):
        """Get total number of reviews"""
        # Check if reviews relation exists
        if hasattr(obj, 'reviews'):
            return obj.reviews.count()
        return 0


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed product serializer"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        source='category', 
        write_only=True
    )
    variants = ProductVariantSerializer(many=True, read_only=True)
    effective_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    discount_percentage = serializers.FloatField(read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    total_stock = serializers.IntegerField(read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    available_sizes = serializers.SerializerMethodField()
    available_colors = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'images', 'price', 
            'discount_price', 'effective_price', 'discount_percentage',
            'is_on_sale', 'category', 'category_id', 'variants', 
            'is_in_stock', 'total_stock', 'average_rating', 
            'review_count', 'available_sizes', 'available_colors',
            'created_at', 'updated_at'
        ]
    
    def get_average_rating(self, obj):
        """Get average rating for the product"""
        # Check if reviews relation exists
        if hasattr(obj, 'reviews'):
            result = obj.reviews.aggregate(Avg('rating'))
            return round(result['rating__avg'], 2) if result['rating__avg'] else 0
        return 0
    
    def get_review_count(self, obj):
        """Get total number of reviews"""
        # Check if reviews relation exists
        if hasattr(obj, 'reviews'):
            return obj.reviews.count()
        return 0
    
    def get_available_sizes(self, obj):
        """Get list of available sizes with stock"""
        sizes = []
        size_variants = obj.variants.values('size__id', 'size__size_name').annotate(
            total_stock=models.Sum('stock_qty')
        ).filter(total_stock__gt=0)
        
        for variant in size_variants:
            sizes.append({
                'id': variant['size__id'],
                'name': variant['size__size_name'],
                'in_stock': variant['total_stock'] > 0
            })
        return sizes
    
    def get_available_colors(self, obj):
        """Get list of available colors with stock"""
        colors = []
        color_variants = obj.variants.values(
            'color__id', 'color__color_name', 'color__hex_code'
        ).annotate(
            total_stock=models.Sum('stock_qty')
        ).filter(total_stock__gt=0)
        
        for variant in color_variants:
            colors.append({
                'id': variant['color__id'],
                'name': variant['color__color_name'],
                'hex_code': variant['color__hex_code'],
                'in_stock': variant['total_stock'] > 0
            })
        return colors
    
    def validate_images(self, value):
        """Validate images field"""
        if isinstance(value, list):
            # Validate each URL
            for url in value:
                if not isinstance(url, str):
                    raise serializers.ValidationError("Each image must be a URL string")
            return value
        elif isinstance(value, str):
            # Convert comma-separated string to list
            urls = [url.strip() for url in value.split(',') if url.strip()]
            return urls
        else:
            raise serializers.ValidationError("Images must be a list of URLs or comma-separated string")


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products"""
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category'
    )
    images = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        help_text="List of image URLs"
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'images', 'price', 
            'discount_price', 'category_id'
        ]
    
    def validate_discount_price(self, value):
        """Validate discount price is less than regular price"""
        if value and self.initial_data.get('price'):
            if value >= self.initial_data.get('price'):
                raise serializers.ValidationError(
                    "Discount price must be less than regular price"
                )
        return value