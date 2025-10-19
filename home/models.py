from django.db import models
from tinymce.models import HTMLField
from accounts.models import CustomUser

class AuditModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(AuditModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, help_text="Hex color code, e.g., #RRGGBB")

    def __str__(self):
        return self.name
    
class ProductImage(AuditModel):
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.alt_text if self.alt_text else f"Image {self.id}"
    
class Product(AuditModel):
    name = models.CharField(max_length=200)
    images = models.ManyToManyField(ProductImage, related_name='products', blank=True)
    description = HTMLField()
    pre_discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
    

class Cart(AuditModel):
    user = models.ForeignKey(CustomUser, related_name='carts', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='carts', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.quantity * self.product.price
    
    def __str__(self):
        return f"Cart of {self.user.username} - {self.product.name} (x{self.quantity})"
    
    def save(self, *args, **kwargs):
        if self.quantity < 1:
            self.delete()
        else:
            super().save(*args, **kwargs)
    
class WishList(AuditModel):
    user = models.ForeignKey(CustomUser, related_name='wishlists', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlists', on_delete=models.CASCADE)
    is_notified = models.BooleanField(default=False)

    def __str__(self):
        return f"Wishlist of {self.user.username} - {self.product.name}"
    
class Order(AuditModel):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(CustomUser, related_name='orders', on_delete=models.CASCADE)
    carts = models.ManyToManyField(Cart, related_name='orders')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    product_code = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_uuid = models.CharField(max_length=100, unique=True)


    def __str__(self):
        return f"Order {self.id} by {self.user.username} - {self.product_code}"
    @property
    def total_price(self):
        return sum(cart.total_price for cart in self.carts.all())
    
    @property
    def total_items(self):
        return sum(cart.quantity for cart in self.carts.all())
    

class Review(AuditModel):
    user = models.ForeignKey(CustomUser, related_name='reviews', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = HTMLField(blank=True, null=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name} - {self.rating} stars"