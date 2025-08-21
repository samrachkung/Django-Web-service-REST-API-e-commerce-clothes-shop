from rest_framework import serializers


class BulkAddToCartSerializer(serializers.Serializer):
    """Serializer for bulk add to cart"""
    items = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )


class SearchQuerySerializer(serializers.Serializer):
    """Serializer for search queries"""
    q = serializers.CharField(required=True, min_length=1)
    type = serializers.ChoiceField(
        choices=['all', 'products', 'categories'],
        default='all'
    )
    limit = serializers.IntegerField(default=10, min_value=1, max_value=100)


class APIStatsSerializer(serializers.Serializer):
    """Serializer for API statistics"""
    products = serializers.DictField()
    orders = serializers.DictField()
    users = serializers.DictField()
    reviews = serializers.DictField()
    timestamp = serializers.DateTimeField()