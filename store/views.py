from os import stat
import re
from site import addusersitepackages
from tkinter import N
import django
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Order, Product
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator  # for Class Based Views
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import requests
import json
import sys
from subprocess import run, PIPE
from django.http import HttpResponseRedirect
from .models import *
from .forms import *
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.template import Context
from django.views.generic import ListView
from django.db.models import Q


# Create your views here.


def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/index.html', context)


def detail(request, slug):

    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(
        is_active=True, category=product.category)[:4]

    headers = {
        'content-type': "multipart/form-data",
        'cache-control': "no-cache",
    }

    recommend = None
    obj_list = []
    product_name = product.title
    print(product_name)
    if product_name:
        url = "http://127.0.0.1:5000/get_recommendation"
        payload = {'product_name': product_name}
        responses = requests.request("POST", url, data=payload)
        print(responses)

        response = json.loads(responses.text)

        print(response)

        value = tuple(response.values())
        print(value)
        for x in value:
            try:
                '''
                    filtering the products database by product title, with respect to
                    the obtained flask recommendation api.
                '''
                recommend = Product.objects.get(title=x)
                obj_list.append(recommend)
            except:

                pass

    context = {

        'product': product,
        'related_products': related_products,
        'recommendated': obj_list

    }
    return render(request, 'store/detail.html', context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories': categories})

# # /////////    NORMAL QUERY SEARCH FOR PRODUCTS    /////////

# def category_products(request, slug):
#     if 'q' in request.GET:
#         q = request.GET['q']
#         category = get_object_or_404(Category, slug=slug)
#         products = Product.objects.filter(title__icontains=q)
#         categories = Category.objects.filter(is_active=True)
#         context = {
#             'category': category,
#             'products': products,
#             'categories': categories,
#         }
#     else:
#         category = get_object_or_404(Category, slug=slug)
#         products = Product.objects.filter(is_active=True, category=category)
#         categories = Category.objects.filter(is_active=True)
#         context = {
#             'category': category,
#             'products': products,
#             'categories': categories,
#         }
#     return render(request, 'store/category_products.html', context)


# //////////////// SEARCH WITH COMMAS AND SAPCING ////////////


def category_products(request, slug):

    if request.method == 'GET':
        query = request.GET.get('q')
        products = None
        count_search = None
        if query:

            for ing in query.split():

                products = Product.objects.filter(
                    Q(title__icontains=ing) | Q(short_description__icontains=ing))
                count_search = products.count()
                print(ing)
        category = get_object_or_404(Category, slug=slug)
        categories = Category.objects.filter(is_active=True)

        context = {
            'category': category,
            'products': products,
            'categories': categories,
            'count_search': count_search,
            'query': query,
        }

    else:
        category = get_object_or_404(Category, slug=slug)
        products = Product.objects.filter(is_active=True, category=category)
        categories = Category.objects.filter(is_active=True)
        context = {
            'category': category,
            'products': products,
            'categories': categories,
        }
    return render(request, 'store/category_products.html', context)


# Authentication Starts Here

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(
                request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, 'account/register.html', {'form': form})


@ login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses': addresses, 'orders': orders})


@ method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user = request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@ login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')


@ login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()

    return redirect('store:cart')


@ login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user == user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@ login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')


@ login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@ login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')


@ login_required
def checkout(request):
    user = request.user
    address_id = request.GET.get('address')
    address = get_object_or_404(Address, id=address_id)

    cart = Cart.objects.filter(user=user)
    for c in cart:
        Order(user=user, address=address,
              product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect('store:orders')


@ login_required
def orders(request):
    all_orders = Order.objects.filter(
        user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})


def shop(request):
    return render(request, 'store/shop.html')


def test(request):
    return render(request, 'store/test.html')


def chkout(request):
    user = request.user
    if request.method == "POST":
        form = contactEnquiry()
        name = request.POST.get('name')
        reciver = request.POST.get('reciver')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        form.name = name
        form.reciver = reciver
        form.email = email
        form.phone = phone
        form.save()
        return redirect('store:checkout')

    addresses = Address.objects.filter(user=user)
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    cp = [p for p in Cart.objects.all() if p.user == user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    context = {

        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/chkout.html', context)

# fro payment API


@ csrf_exempt
def verify_payment(request):
    data = request.POST
    product_id = data['product_identity']
    token = data['token']
    amount = data['amount']

    url = "https://khalti.com/api/v2/payment/verify/"
    payload = {
        "token": token,
        "amount": amount,
    }
    headers = {
        "Authorization": "Key test_secret_key_dd9644e41839430a8e9e71627b23ce6b"
    }

    response = requests.post(url, payload, headers=headers)

    response_data = json.loads(response.text)
    status_code = str(response.status_code)

    if status_code == '400':
        response = JsonResponse(
            {'status': 'false', 'message': response_data['detail']}, status=500)
        return response

    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(response_data)

    return JsonResponse(f"Payment Done !! With IDX. {response_data['user']['idx']}", safe=False)


@ login_required
def blog(request):
    blogs = Blog.objects.all()[:6]
    return render(request, "store/blog.html", {"blogs": blogs})


@ login_required
def post_detail(request, slug):
    post = get_object_or_404(Blog, slug=slug)
    related_blog = Blog.objects.exclude(title=post.title)

    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()

            return redirect('post_detail', slug=post.slug)

    else:
        form = ReviewForm()

    return render(request, 'store/post_detail.html', {'post': post, 'related_blog': related_blog, 'form': form})


# recommendation part


# for Email API

def contact(request):
    username = None
    if request.user.is_authenticated():
        username = request.user.username
        useremail = request.user.email
        if request.method == "POST":
            message_name = username
            message_email = useremail
            message = 'hello help me'

            send_mail(
                'message from' + message_name,
                message,
                message_email,
                ['fypusphot@gmail.com', 'awalupshot@gmail.com'],
            )
            return render(request, 'contact.html', {'message_name': message_name})
        else:
            return render(request, 'contact.html')


# def external(request):
#     out = run([sys.executable, '/script.py'], shell=False, stdout=PIPE)
#     print(out)
#     return render(request, 'store/index.html', {'data1': out.stdout})


def rate(request):
    if request.method == 'POST':
        el_id = request.POST.get('el_id')
        val = request.POST.get('val')
        obj = Rating.objects.get(id=el_id)
        obj.score = val
        obj.save()
        return JsonResponse({'success': 'true', 'score': val}, safe=False)
    return JsonResponse({'success': 'false'})
