# reviews/serializers.py
from rest_framework import serializers
from .models import Review
from accounts.models import User
from products.models import Product


class ReviewUserSerializer(serializers.ModelSerializer):
    """Nested serializer for user info in reviews"""
    class Meta:
        model = User
        fields = ['id', 'name', 'email']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reading reviews"""
    user = ReviewUserSerializer(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    time_since = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'product', 'product_id', 'product_name', 
            'user', 'rating', 'comment', 
            'created_at', 'updated_at', 'time_since'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_time_since(self, obj):
        """Calculate time since review was created"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 365:
            return f"{diff.days // 365} year{'s' if diff.days // 365 > 1 else ''} ago"
        elif diff.days > 30:
            return f"{diff.days // 30} month{'s' if diff.days // 30 > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hour{'s' if diff.seconds // 3600 > 1 else ''} ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minute{'s' if diff.seconds // 60 > 1 else ''} ago"
        else:
            return "Just now"


class CreateReviewSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating reviews"""
    class Meta:
        model = Review
        fields = ['product', 'rating', 'comment']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate_comment(self, value):
        """Validate comment is not empty and has minimum length"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Comment must be at least 10 characters long")
        return value.strip()
    
    def validate(self, attrs):
        """Additional validation"""
        request = self.context.get('request')
        if request and request.user:
            product = attrs.get('product')
            
            # Check if user already reviewed this product (for create action)
            if self.instance is None:  # Creating new review
                existing_review = Review.objects.filter(
                    user=request.user,
                    product=product
                ).exists()
                
                if existing_review:
                    raise serializers.ValidationError(
                        "You have already reviewed this product"
                    )
        
        return attrs