from django.shortcuts import render,redirect
from django.views import View
from .models import Customer,Product,Cart,OrderPlaced
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class ProductViews(View):
    def get(self,request):
        totalitem =0
        streetwear = Product.objects.filter(category='s')
        koreanwear = Product.objects.filter(category='k')
        formalwear = Product.objects.filter(category='f')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request,'app/home.html',{'streetwear':streetwear,
        'koreanwear':koreanwear,'formalwear':formalwear,'totalitem':totalitem})

#def home(request):
# return render(request, 'app/home.html')

#def product_detail(request):
#return render(request, 'app/productdetail.html')

class ProductDetailView(View):
    def get(self,request,pk):
        totalitem = 0
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request,'app/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart,'totalitem':totalitem})

@login_required
def add_to_cart(request):
    user =request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect('/cart')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                totalamount = amount + shipping_amount
            return render(request, 'app/addtocart.html',{'carts':cart,'amount':amount,'totalamount':totalamount,'totalitem':totalitem})
        else:
            return render(request,'app/emptycart.html')   

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.quantity+=1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.quantity-=1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data) 


def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'amount':amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data)              

@login_required
def buy_now(request):
 return render(request, 'app/buynow.html')

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})

    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            provience = form.cleaned_data['provience']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr,name=name,locality=locality,city=city,provience=provience,zipcode=zipcode)
            reg.save()
            messages.success(request,'Congratulation!! Profile Updated Successfully')
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})    



#def passwordreset(request):
    #return render(request,'app/passwordreset.html') 
@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    totalitem =0
    if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/address.html',{'add':add,'active':'btn-primary','totalitem':totalitem})

@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/orders.html',{'order_placed':op,'totalitem':totalitem})



def koreanwear(request,data=None):
    if data == None:
        koreanwear = Product.objects.filter(category='k')
    elif data == 'UNIQ' or data=='abcd':
        koreanwear = Product.objects.filter(category='k').filter(brand=data)
    elif data == 'below':
        koreanwear = Product.objects.filter(category='k').filter(selling_price = 1000)
    elif data == 'above':
        koreanwear = Product.objects.filter(category='k').filter(selling_price = 5000)        
    return render(request, 'app/koreanwear.html',{'koreanwear':koreanwear})

class customerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html',{'form':form})
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'Congratulation !! Registered Successfully')
            form.save()
        return render(request,'app/customerregistration.html',{'form':form})    

@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    totalitem = 0 
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount +=tempamount
        totalamount = amount + shipping_amount   
    return render(request, 'app/checkout.html',{'add':add,'totalamount':totalamount,'cart_items':cart_items,'totalitem':totalitem})

def formalwear(request,data=None):
    if data == None:
        formalwear = Product.objects.filter(category='f')
    elif data == 'UNIQ' or data=='abcd':
        formalwear = Product.objects.filter(category='f').filter(brand=data)
    elif data == 'below':
        formalwear = Product.objects.filter(category='f').filter(selling_price = 1000)
    elif data == 'above':
        formalwear = Product.objects.filter(category='f').filter(selling_price = 5000)        
    return render(request, 'app/formalwear.html',{'formalwear':formalwear})

def streetwear(request,data=None):
    if data == None:
        streetwear = Product.objects.filter(category='s')
    elif data == 'LOCO' or data=='KP':
        streetwear = Product.objects.filter(category='s').filter(brand=data)
    elif data == 'below':
        streetwear = Product.objects.filter(category='s').filter(selling_price = 1000)
    elif data == 'above':
        streetwear = Product.objects.filter(category='s').filter(selling_price = 5000)        
    return render(request, 'app/streetwear.html',{'streetwear':streetwear})  

@login_required
def paymentdone(request):
    user = request.user
    custid = request.GET.get('custid')  
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
        c.delete()
    return redirect('orders')     


 

