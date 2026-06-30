from django.shortcuts import render, redirect, get_object_or_404 
from .models import Product, Order, OrderItem, Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from .forms import RegisterForm, ProductForm


# ================= HOME =================
# Only logged-in users can access home
@login_required
def home(request):
    return render(request, 'home.html')


# ================= PRODUCT LIST =================
# Display all products
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})


# ================= ORDER LIST =================
# Show user's previous orders
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders.html', {'orders': orders})


# ================= ADD PRODUCT =================
# Add new product (admin-like functionality)
@login_required
def add_product(request):
    form = ProductForm()

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products')

    return render(request, 'add_product.html', {'form': form})


# ================= REGISTER =================
# User registration
def register(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
           user = form.save(commit=False)
           user.set_password(form.cleaned_data['password'])  # Encrypt password
           user.save()
           return redirect('login')

    return render(request, 'register.html', {'form': form})


# ================= LOGIN =================
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid login")

    return render(request, 'login.html')


# ================= LOGOUT =================
def user_logout(request):
    logout(request)
    return redirect('login')


# ================= DASHBOARD =================
@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user)
    products = Product.objects.all()

    return render(request, 'dashboard.html', {
        'orders': orders,
        'products': products
    })


# ================= ADD TO CART =================
@login_required
def add_to_cart(request, product_id):
    # Safely get product (prevents crash if invalid ID)
    product = get_object_or_404(Product, id=product_id)

    # Validation: prevent adding out-of-stock items
    if product.stock <= 0:
        messages.error(request, "Product out of stock")
        return redirect('products')

    # Get or create cart (Order)
    order, created = Order.objects.get_or_create(
        user=request.user,
        complete=False
    )

    # Get or create cart item
    item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={'quantity': 1}
    )

    # If already exists → increase quantity
    if not created:
        item.quantity += 1
        item.save()

    return redirect('products')


# ================= VIEW CART =================
@login_required
def cart(request):
    # Get or create cart safely
    order, created = Order.objects.get_or_create(
        user=request.user,
        complete=False
    )

    # Get all items in cart
    items = OrderItem.objects.filter(order=order)

    # Calculate total price for each item
    for item in items:
        item.total_price = item.product.price * item.quantity

    # Calculate grand total
    total = sum(item.total_price for item in items)

    return render(request, 'cart.html', {
        'items': items,
        'total': total
    })


# ================= REMOVE ITEM =================
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)

    # Security: ensure item belongs to logged-in user
    if item.order.user != request.user:
        return redirect('cart')

    item.delete()
    return redirect('cart')


# ================= INCREASE QUANTITY =================
@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)

    # Security check
    if item.order.user != request.user:
        return redirect('cart')

    item.quantity += 1
    item.save()
    return redirect('cart')


# ================= DECREASE QUANTITY =================
@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)

    # Security check
    if item.order.user != request.user:
        return redirect('cart')

    # If quantity > 1 → decrease
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        # If quantity = 1 → remove item
        item.delete()

    return redirect('cart')



# ================= SESSION CART ADD =================
def add_to_session_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': 1
        }

    request.session['cart'] = cart
    return redirect('session_cart')


# ================= SESSION CART VIEW =================
def session_cart(request):
    cart = request.session.get('cart', {})
    total = 0

    for item in cart.values():
        item['total'] = item['price'] * item['quantity']
        total += item['total']

    return render(request, 'session_cart.html', {
        'cart': cart,
        'total': total
    })


# ================= REMOVE SESSION ITEM =================
def remove_session_item(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]

    request.session['cart'] = cart
    return redirect('session_cart')



#Order CRUD:
@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user != request.user:
        return redirect('orders')

    order.status = 'Delivered'
    order.save()

    return redirect('orders')


@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user != request.user:
        return redirect('orders')

    order.delete()
    return redirect('orders')




#profile CRUD:
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})


@login_required
def update_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.save()
        return redirect('profile')

    return render(request, 'update_profile.html', {'profile': profile})



@login_required
def checkout(request):
    order = Order.objects.get(user=request.user, complete=False)
    order.complete = True
    order.save()

    return redirect('orders')