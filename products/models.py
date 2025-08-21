# products/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField


class Category(models.Model):
    """Product category model"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
        db_table = 'categories'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model with image URLs"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Store multiple image URLs as JSON array or text field
    # Option 1: JSONField for PostgreSQL/SQLite 3.9+
    images = JSONField(default=list, blank=True, help_text="List of image URLs")
    
    # Option 2: If JSONField doesn't work, use TextField with comma separation
    # images = models.TextField(blank=True, help_text="Comma-separated image URLs")
    
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    discount_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0)]
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'products'
    
    def __str__(self):
        return self.name
    
    @property
    def effective_price(self):
        """Get the effective price (discount price if available)"""
        return self.discount_price if self.discount_price else self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.discount_price and self.price > 0:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return round(discount, 2)
        return 0
    
    @property
    def primary_image(self):
        """Get the first image URL"""
        if isinstance(self.images, list) and self.images:
            return self.images[0]
        elif isinstance(self.images, str) and self.images:
            # If images are stored as comma-separated string
            urls = [url.strip() for url in self.images.split(',')]
            return urls[0] if urls else None
        return None
    
    @property
    def is_on_sale(self):
        """Check if product is on sale"""
        return self.discount_price is not None and self.discount_price < self.price
    
    @property
    def total_stock(self):
        """Get total stock across all variants"""
        return self.variants.aggregate(
            total=models.Sum('stock_qty')
        )['total'] or 0
    
    @property
    def is_in_stock(self):
        """Check if any variant is in stock"""
        return self.variants.filter(stock_qty__gt=0).exists()


class Size(models.Model):
    """Size options for products"""
    size_name = models.CharField(max_length=10, unique=True)
    
    class Meta:
        ordering = ['size_name']
        db_table = 'sizes'
    
    def __str__(self):
        return self.size_name


class Color(models.Model):
    """Color options for products"""
    color_name = models.CharField(max_length=30, unique=True)
    hex_code = models.CharField(
        max_length=7, 
        blank=True, 
        null=True,
        help_text="Hex color code (e.g., #FF0000)"
    )
    
    class Meta:
        ordering = ['color_name']
        db_table = 'colors'
    
    def __str__(self):
        return self.color_name


class ProductVariant(models.Model):
    """Product variants with size and color combinations"""
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='variants'
    )
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    stock_qty = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['product', 'size', 'color']
        ordering = ['size__size_name', 'color__color_name']
        db_table = 'product_variants'
    
    def __str__(self):
        return f"{self.product.name} - {self.size.size_name} - {self.color.color_name}"
    
    @property
    def is_in_stock(self):
        return self.stock_qty > 0
    
    @property
    def variant_name(self):
        return f"{self.size.size_name} / {self.color.color_name}"