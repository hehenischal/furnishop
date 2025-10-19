from django.shortcuts import render,redirect
from .models import Cart, Product,Category,Order
import uuid
from django_esewa import EsewaPayment

def home(request):
    products = Product.objects.all()
    new_arrivals = products.order_by('-created_at')[:10]
    categories = Category.objects.all()
    context = {
        'products': products,
        'new_arrivals': new_arrivals,
        'categories': categories
    }
    return render(request, 'home.html',context)

def product_page(request,id):
    product = Product.objects.get(id=id)
    ratings = product.reviews.all() # type: ignore
    rating = 0 
    for r in ratings:
        rating += r.rating

    if ratings:
        rating /= ratings.count()
        rating = round(rating)
    context = {
        'product': product,
        'rating': rating,
        'ratings': ratings
    }
    return render(request, 'product.html',context)

def add_to_cart(request,id):
    if request.method == 'POST':
        product = Product.objects.get(id=id)
        quantity = int(request.POST.get('qty', 1))
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product, is_active=True)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        http_referrer = request.META.get('HTTP_REFERER', '/')
        return redirect(http_referrer)
    
def remove_from_cart(request,id):
    print(request.POST)
    if request.method == 'POST':
        product = Product.objects.get(id=id)
        cart_item = Cart.objects.filter(user=request.user, product=product, is_active=True).first()
        if cart_item:
            cart_item.quantity -= 1
            if cart_item.quantity <= 0:
                cart_item.delete()
            else:
                cart_item.save()
        http_referrer = request.META.get('HTTP_REFERER', '/')
        return redirect(http_referrer)


def cart(request):
    cart_items = Cart.objects.filter(user=request.user, is_active=True)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    context = {
        'carts': cart_items,
        'total_price': total_price
    }
    return render(request, 'cart.html', context)

def checkout(request):
    cart_items = Cart.objects.filter(user=request.user, is_active=True)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    obj = Order.objects.create(
        user=request.user, 
        product_code="EPAYTEST", 
        amount=total_price, 
        tax_amount=0, 
        total_amount=total_price, 
        delivery_charge=0, 
        service_charge=0, 
        transaction_uuid=uuid.uuid4()
    )
    obj.carts.set(cart_items)
    obj.save()
    payment = EsewaPayment(
        product_code=obj.product_code,
        success_url=f"http://localhost:8000/success/{obj.transaction_uuid}/",
        failure_url=f"http://localhost:8000/failure/{obj.transaction_uuid}/",
        amount= obj.amount, # type: ignore
        tax_amount=0,
        total_amount=obj.total_amount, # type: ignore
        product_delivery_charge=obj.delivery_charge, # type: ignore
        product_service_charge=obj.service_charge, # type: ignore
        transaction_uuid=obj.transaction_uuid,
        secret_key="8gBm/:&EnhH.1/q",
    )
    payment.create_signature()
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'form': payment.generate_form()
    }
    return render(request, 'checkout.html', context)



def success(request,transaction_uuid):

    order = Order.objects.get(transaction_uuid=transaction_uuid)
    obj = order
    payment = EsewaPayment(
        product_code=obj.product_code,
        success_url=f"http://localhost:8000/success/{obj.transaction_uuid}/",
        failure_url=f"http://localhost:8000/failure/{obj.transaction_uuid}/",
        amount= obj.amount, # type: ignore
        tax_amount=0,
        total_amount=obj.total_amount, # type: ignore
        product_delivery_charge=obj.delivery_charge, # type: ignore
        product_service_charge=obj.service_charge, # type: ignore
        transaction_uuid=obj.transaction_uuid,
        secret_key="8gBm/:&EnhH.1/q",
    )
    if payment.is_completed(dev=True):
        order.status = 'COMPLETED'
        order.save()
        cart_items = Cart.objects.filter(user=request.user, is_active=True)
        for item in cart_items:
            item.is_active = False
            item.save()
        return render(request, 'success.html')
    else:
        return redirect('failure', transaction_uuid=transaction_uuid)
    

def failure(request,transaction_uuid):
    order = Order.objects.get(transaction_uuid=transaction_uuid)
    order.status = 'CANCELLED'
    order.save()
    return render(request, 'failure.html')


