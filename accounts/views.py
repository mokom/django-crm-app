from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from .decorators import unauthenticated_user, allowed_users, admin_only
from .models import *
from .forms import CreateUserForm, OrderForm, CustomerForm
from .filters import OrderFilter

@unauthenticated_user
def registerPage(request):
	form = CreateUserForm()

	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			
			# group = Group.objects.get(name='customer')
			# user.groups.add(group)
			# # Added username after video because of error returning customer name if not added
			# Customer.objects.create(user=user, name=user.username)
			messages.success(request, 'Account was created for ' + username)
			return redirect('accounts:login')
			
	context = {'form': form}
	return render(request, 'accounts/register.html', context)

@unauthenticated_user
def loginPage(request):
	context = {}
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		
		user = authenticate(request, username=username, password=password)
		
		if user is not None:
			login(request, user)
			return redirect('accounts:home')
		else:
			messages.info(request, 'Username OR password in incorrect')
			return render(request, 'accounts/login.html', context)
	
	return render(request, 'accounts/login.html', context)

def logoutUser(request):
	logout(request)
	return redirect("accounts:home")


@login_required(login_url='accounts:login')
@admin_only
def home(request):
	orders = Order.objects.all()
	customers = Customer.objects.all()

	total_customers = customers.count()

	total_orders = orders.count()
	delivered = orders.filter(status='Delivered').count()
	pending = orders.filter(status='Pending').count()
	context = {
		'orders': orders,
		'customers': customers,
		'total_customers': total_customers,
		'total_orders': total_orders,
		'delivered': delivered,
		'pending': pending
	}
	return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
	orders = request.user.customer.order_set.all()
	
	total_orders = orders.count()
	delivered = orders.filter(status='Delivered').count()
	pending = orders.filter(status='Pending').count()
	context = {
		'orders': orders,
		'total_orders': total_orders,
		'delivered': delivered,
		'pending': pending
	}
	return render(request, 'accounts/user.html', context)


@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)
	
	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES, instance=customer)
		if form.is_valid():
			form.save()

	context = {
		'form': form
	}
	return render(request, 'accounts/account_settings.html', context)


@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['admin'])
def products(request):
	context = {
		'products': Product.objects.all()
	}
	return render(request, 'accounts/products.html', context)

@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['admin'])
def customers(request, pk):
	customer = Customer.objects.get(id=pk)
	orders = customer.order_set.all()
	myFilter = OrderFilter(request.GET, queryset=orders)
	orders = myFilter.qs
	context = {
		'customer': customer,
		'orders': orders,
		'myFilter': myFilter
	}
	return render(request, 'accounts/customers.html', context)

@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
	OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=10)
	customer = Customer.objects.get(id=pk)
	formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
	# form = OrderForm(initial={'customer': customer})
	if request.method == 'POST':
		# form = OrderForm(request.POST)
		formset = OrderFormSet(request.POST, instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('accounts:home')
	context = {
		# 'form': form,
		'formset': formset
	}
	return render(request, 'accounts/order_form.html', context)

@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
	order = Order.objects.get(id=pk)
	OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'))
	customer = Customer.objects.get(id=order.customer.id)
	formset = OrderFormSet(instance=customer)
	print("order is: ", order)
	print("customer is: ", customer)
	# order = Order.objects.get(id=pk)
	# form = OrderForm(instance=order)

	if request.method == 'POST':
		formset = OrderFormSet(request.POST, instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('accounts:home')

	context = {
		'formset': formset
	}
	return render(request, 'accounts/order_form.html', context)

@login_required(login_url='accounts:login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == 'POST':
		order.delete()
		return redirect('accounts:home')
	context = {
		'item': order
	}
	return render(request, 'accounts/delete.html', context)