from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product, Category,Order
from django.contrib import messages
from django.utils.crypto import get_random_string
from random import sample
from django.http import HttpResponseForbidden


def home(request):
    products = list(Product.objects.all())
    daily_specials = sample(products, min(2, len(products))) 
    return render(request, 'home.html', {'daily_specials': daily_specials})


def about(request):
    return render(request, 'about.html')



def menu(request):
    categories = Category.objects.all()
    selected_category_id = request.GET.get('category')
    selected_category = None

    if selected_category_id:
        try:
            selected_category = Category.objects.get(id=selected_category_id)
            products = Product.objects.filter(category=selected_category)
        except Category.DoesNotExist:
            products = Product.objects.none()
    else:
        products = Product.objects.all()

    return render(request, 'menu.html', {
        'categories': categories,
        'products': products,
        'selected_category': selected_category,
    })



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = request.session.get('cart', {})

    quantity = int(request.POST.get('quantity', 1))

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': product.price,
            'image_url': product.image_url,
            'quantity': quantity
        }

    request.session['cart'] = cart

    messages.success(request, f"✅ {product.name} was added to your cart!")
    return redirect('menu')


# Remove from cart
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart')


def cart(request):
    cart = request.session.get('cart', {})
    total = 0
    for item in cart.values():
        item['subtotal'] = item['price'] * item['quantity']
        total += item['subtotal']
    return render(request, 'order_summary.html', {'cart': cart, 'total': total})




def unified_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')


def admin_logout(request):
    logout(request)
    return redirect('home')

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('admin_login')
    products = Product.objects.all()
    return render(request, 'admin/dashboard.html', {'products': products})



@login_required
def add_product(request):
    if not request.user.is_staff:
        return redirect('admin_login')

    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = float(request.POST['price'])
        image_url = request.POST['image_url']
        category_id = request.POST['category']
        category = get_object_or_404(Category, id=category_id)

        Product.objects.create(
            name=name,
            description=description,
            price=price,
            image_url=image_url,
            category=category
        )
        return redirect('admin_dashboard')

    return render(request, 'admin/add_product.html', {'categories': categories})


@login_required
def edit_product(request, product_id):
    if not request.user.is_staff:
        return redirect('admin_login')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.price = float(request.POST['price'])
        product.image_url = request.POST['image_url']
        product.category_id = request.POST['category']
        product.save()
        return redirect('admin_dashboard')

    categories = Category.objects.all()
    return render(request, 'admin/edit_product.html', {'product': product, 'categories': categories})

@login_required
def delete_product(request, product_id):
    if not request.user.is_staff:
        return redirect('admin_login')

    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('admin_dashboard')




def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    total = sum(item['price'] * item['quantity'] for item in cart.values())
    session_id = request.session.session_key or get_random_string(32)

    order = Order.objects.create(
        session_id=session_id,
        items=cart,
        total_price=total,
    )

    request.session['cart'] = {}  # clear cart
    return render(request, 'order_placed.html', {'order': order})


def update_cart_quantity(request, product_id):
    if request.method == 'POST':
        new_qty = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            if new_qty > 0:
                cart[str(product_id)]['quantity'] = new_qty
            else:
                del cart[str(product_id)]  # remove if set to 0
            request.session['cart'] = cart
    return redirect('cart')




from django.contrib.auth.models import User

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('home')
    return render(request, 'auth/signup.html')

