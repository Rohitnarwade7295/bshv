from django.shortcuts import render, redirect, HttpResponse
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class ProductView(View):
	def get(self, request):
		totalitem = 0
		desktop = Product.objects.filter(category='DP')
		laptops = Product.objects.filter(category='LP')
		accessories = Product.objects.filter(category='AC')
		if request.user.is_authenticated:
			totalitem = len(Cart.objects.filter(user=request.user))
		return render(request, 'app/home.html', {'desktop':desktop, 'laptops':laptops, 'accessories':accessories, 'totalitem':totalitem})

class ProductDetailView(View):
	def get(self, request, pk):
		totalitem = 0
		product = Product.objects.get(pk=pk)
		print(product.id)
		item_already_in_cart=False
		if request.user.is_authenticated:
			totalitem = len(Cart.objects.filter(user=request.user))
			item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
		return render(request, 'app/productdetail.html', {'product':product, 'item_already_in_cart':item_already_in_cart, 'totalitem':totalitem})

@login_required()
def add_to_cart(request):
	user = request.user
	item_already_in_cart1 = False
	product = request.GET.get('prod_id')
	item_already_in_cart1 = Cart.objects.filter(Q(product=product) & Q(user=request.user)).exists()
	if item_already_in_cart1 == False:
		product_title = Product.objects.get(id=product)
		Cart(user=user, product=product_title).save()
		messages.success(request, 'Product Added to Cart Successfully !!' )
		return redirect('/cart')
	else:
		return redirect('/cart')
  # Below Code is used to return to same page
  # return redirect(request.META['HTTP_REFERER'])

@login_required
def show_cart(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))
		user = request.user
		cart = Cart.objects.filter(user=user)
		amount = 0.0
		totalamount=0.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		print(cart_product)
		if cart_product:
			for p in cart_product:
				tempamount = (p.quantity * p.product.discounted_price)
				amount += tempamount
			shipping_amount= 0.0 if amount==0 else 70.0
			totalamount = amount+shipping_amount
			
			return render(request, 'app/addtocart.html', {'carts':cart, 'amount':amount, 'totalamount':totalamount, 'totalitem':totalitem,'shippingAmount':shipping_amount})
		else:
			return render(request, 'app/emptycart.html', {'totalitem':totalitem})
	else:
		return render(request, 'app/emptycart.html', {'totalitem':totalitem})

def plus_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.quantity+=1
		c.save()
		amount = 0.0
		
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			# print("Quantity", p.quantity)
			# print("Selling Price", p.product.discounted_price)
			# print("Before", amount)
			amount += tempamount
			# print("After", amount)
		# print("Total", amount)
		shipping_amount= 0.0 if amount==0 else 70.0
		data = {
			'quantity':c.quantity,
			'amount':amount,
			'totalamount':amount+shipping_amount,
			'shippingAmount':shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")

def minus_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.quantity-=1
		if c.quantity>0:
			c.save()
		else:
			c.quantity=1
			c.save()
		amount = 0.0
		
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			# print("Quantity", p.quantity)
			# print("Selling Price", p.product.discounted_price)
			# print("Before", amount)
			amount += tempamount
			# print("After", amount)
		# print("Total", amount)
		shipping_amount= 0.0 if amount==0 else 70.0
		data = {
			'quantity':c.quantity,
			'amount':amount,
			'totalamount':amount+shipping_amount,
			'shippingAmount':shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")

@login_required
def checkout(request):
	user = request.user
	add = Customer.objects.filter(user=user)
	cart_items = Cart.objects.filter(user=request.user)
	return render(request, 'app/checkout.html', {'add':add, 'cart_items':cart_items})

@login_required
def payment_done(request):
	custid = request.GET.get('custid')
	print("Customer ID", custid)
	user = request.user
	cartid = Cart.objects.filter(user = user)
	customer = Customer.objects.get(id=custid)
	print(customer)
	for cid in cartid:
		OrderPlaced(user=user, customer=customer, product=cid.product, quantity=cid.quantity).save()
		print("Order Saved")
		cid.delete()
		print("Cart Item Deleted")
	return redirect("orders")

def remove_cart(request):
	if request.method == 'GET':
		prod_id = request.GET['prod_id']
		c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
		c.delete()
		amount = 0.0

		shipping_amount= 0.0 if amount==0 else 70.0
		cart_product = [p for p in Cart.objects.all() if p.user == request.user]
		for p in cart_product:
			tempamount = (p.quantity * p.product.discounted_price)
			# print("Quantity", p.quantity)
			# print("Selling Price", p.product.discounted_price)
			# print("Before", amount)
			amount += tempamount
			# print("After", amount)
		# print("Total", amount)
		data = {
			'amount':amount,
			'totalamount':amount+shipping_amount,
			'shippingAmount':shipping_amount
		}
		return JsonResponse(data)
	else:
		return HttpResponse("")

@login_required
def address(request):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))
	add = Customer.objects.filter(user=request.user)
	return render(request, 'app/address.html', {'add':add, 'active':'btn-primary', 'totalitem':totalitem})

@login_required
def orders(request):
	op = OrderPlaced.objects.filter(user=request.user)
	return render(request, 'app/orders.html', {'order_placed':op})


def laptops(request, data=None):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))
	if data==None :
			laptops = Product.objects.filter(category='LP')
	elif data == 'HP' or data == 'DELL' or data == 'APPLE' or data == 'ACER' or data == 'MSI':
			laptops = Product.objects.filter(category='LP').filter(brand=data)
	elif data == 'below':
			laptops = Product.objects.filter(category='LP').filter(discounted_price__lt=10000)
	elif data == 'above':
			laptops = Product.objects.filter(category='LP').filter(discounted_price__gt=10000)
	return render(request, 'app/laptops.html', {'laptops':laptops, 'totalitem':totalitem})


def desktops(request, data=None):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))
	if data==None :
			desktops = Product.objects.filter(category='DP')
	elif data == 'HP' or data == 'DELL' or data == 'APPLE' or data == 'ACER' or data == 'MSI':
			desktops = Product.objects.filter(category='DP').filter(brand=data)
	elif data == 'below':
			desktops = Product.objects.filter(category='DP').filter(discounted_price__lt=10000)
	elif data == 'above':
			desktops = Product.objects.filter(category='DP').filter(discounted_price__gt=10000)
	return render(request, 'app/desktops.html', {'desktops':desktops, 'totalitem':totalitem})

def accessories(request, data=None):
	totalitem = 0
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))
	if data==None :
			accessories = Product.objects.filter(category='AC')
	elif data == 'Monitor' or data == 'Mouse' or data == 'Keyboard' or data == 'Speacker' or data == 'Mice' or data == 'Motherboard' or 'Pendrive'  or data == 'Hardisk':
			accessories = Product.objects.filter(category='AC').filter(brand=data)
	elif data == 'below':
			accessories = Product.objects.filter(category='AC').filter(discounted_price__lt=10000)
	elif data == 'above':
			accessories = Product.objects.filter(category='AC').filter(discounted_price__gt=10000)
	return render(request, 'app/accessories.html', {'accessories':accessories, 'totalitem':totalitem})


class CustomerRegistrationView(View):
 def get(self, request):
  form = CustomerRegistrationForm()
  return render(request, 'app/customerregistration.html', {'form':form})
  
 def post(self, request):
  form = CustomerRegistrationForm(request.POST)
  if form.is_valid():
   messages.success(request, 'Congratulations!! Registered Successfully.')
   form.save()
  return render(request, 'app/customerregistration.html', {'form':form})

def search(request, data=None):
	totalitem = 0
	data1=request.POST.get('data')
	print(data)
	
	if request.user.is_authenticated:
		totalitem = len(Cart.objects.filter(user=request.user))
	if data1==None or data=="":
			search = Product.objects.all()
	else:
		search = Product.objects.filter(title__icontains=data1)

	return render(request, 'app/search.html', {'search':search, 'totalitem':totalitem})



def singlecheck(request,data=None):
	user = request.user
	add = Customer.objects.filter(user=user)
	cart_items = Product.objects.filter(pk=18)
	amount = 0.0
	shipping_amount = 70.0
	totalamount=0.0
	totalamount = 10
	return render(request, 'app/checkout.html', {'add':add, 'cart_items':cart_items, 'totalcost':totalamount})

@login_required
def payment_done(request):
	custid = request.GET.get('custid')
	print("Customer ID", custid)
	user = request.user
	cartid = Cart.objects.filter(user = user)
	customer = Customer.objects.get(id=custid)
	print(customer)
	for cid in cartid:
		OrderPlaced(user=user, customer=customer, product=cid.product, quantity=cid.quantity).save()
		print("Order Saved")
		cid.delete()
		print("Cart Item Deleted")
	return redirect("orders")

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
	def get(self, request):
		totalitem = 0
		if request.user.is_authenticated:
			totalitem = len(Cart.objects.filter(user=request.user))
		form = CustomerProfileForm()
		return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary', 'totalitem':totalitem})
		
	def post(self, request):
		totalitem = 0
		if request.user.is_authenticated:
			totalitem = len(Cart.objects.filter(user=request.user))
		form = CustomerProfileForm(request.POST)
		if form.is_valid():
			usr = request.user
			name  = form.cleaned_data['name']
			locality = form.cleaned_data['locality']
			city = form.cleaned_data['city']
			state = form.cleaned_data['state']
			zipcode = form.cleaned_data['zipcode']
			reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
			reg.save()
			messages.success(request, 'Congratulations!! Profile Updated Successfully.')
		return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary', 'totalitem':totalitem})
