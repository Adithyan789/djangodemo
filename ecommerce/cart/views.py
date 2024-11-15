from django.shortcuts import render,redirect
from shop.models import Product
from cart.models import Cart,Payment,Order_details
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
import razorpay
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@login_required
def addtocart(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    try:
        c=Cart.objects.get(product=p,user=u)    #checks the product present in cart table for the particular user
        if(p.stock>0):
            c.quantity+=1                        #if present it will increment the quantity of that particular product
            c.save()
            p.stock-=1
            p.save()

    except:
        if (p.stock > 0):
            c=Cart.objects.create(product=p,user=u,quantity=1)
            c.save()
            p.stock -= 1
            p.save()
            
    return redirect('cart:cartview')

@login_required
def cart_view(request):
    u=request.user
    #if particular product for a particular user already exists
    c=Cart.objects.filter(user=u)
    total=0

    for i in c:
        total+=i.quantity*i.product.price


    context={'cart':c,'total':total}

    return render(request,'cart.html',context)

@login_required
def cart_remove(request,i):
    p=Product.objects.get(id=i)
    u=request.user

    try:
        c=Cart.objects.get(product=p,user=u)
        if(c.quantity > 1):
            c.quantity-=1
            c.save()
            p.stock+=1
            p.save()

        else:
            c.delete()
            p.stock+=1
            p.save()

    except:
        pass
    return redirect('cart:cartview')


@login_required
def cart_delete(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    c=Cart.objects.get(product=p,user=u)
    c.delete()
    p.stock+=c.quantity
    p.save()

    return redirect('cart:cartview')

@login_required
def order_form(request):
    if(request.method=='POST'):
        a=request.POST['a']
        ph=request.POST['ph']
        pi=request.POST['pi']
        u=request.user
        c=Cart.objects.filter(user=u)
        total=0
        for i in c:
            total+=i.quantity*i.product.price
        total1=int(total*100)
        # print(total)

        client=razorpay.Client(auth=('rzp_test_RbrhgeNE0WBB2W','mYhbXbCmP3ueeoIp0uCLIomZ'))  #creates a client connection using razorpay id and secret code.

        response_payment=client.order.create(dict(amount=total1,currency="INR"))    #creates an order with razorpay using razorpay client.

        # print(response_payment)

        order_id=response_payment['id']   #retrives the order id from response
        status=response_payment['status']   #retrives the status from response

        if(status=='created'):    #if status is created the store order_id in the Payment and Order_details Table.
            p=Payment.objects.create(name=u.username,amount=total,order_id=order_id)
            p.save()
            for i in c:     #for each item creates a record inside Order_details table
                o=Order_details.objects.create(product=i.product,user=u,no_of_items=i.quantity,address=a,phone=ph,pin=pi,order_id=order_id)
                o.save()

        response_payment['name']=u.username
        context={'payment':response_payment}

        return render(request,'payment.html',context)

    return render(request,'order.html')


@csrf_exempt
def payment_status(request,u):
    usr = User.objects.get(username=u)
    if not request.user.is_authenticated:
        login(request,usr)
    # print(u)

    if(request.method=='POST'):
        response=request.POST
        print(response)

        param_dict={
            'razorpay_payment_id':response['razorpay_payment_id'],
            'razorpay_order_id':response['razorpay_order_id'],
            'razorpay_signature':response['razorpay_signature']
        }

        #To check the authenticity of the Razorpay Signature
        client = razorpay.Client(auth=('rzp_test_RbrhgeNE0WBB2W', 'mYhbXbCmP3ueeoIp0uCLIomZ'))
        # print(client)

        try:
            status=client.utility.verify_payment_signature(param_dict)
            print(status)

         #To retrive a particular record from Payment table matching with razorpay response order id
            p=Payment.objects.get(order_id=response['razorpay_order_id'])
            p. razorpay_payment_id=response['razorpay_payment_id']
            p.paid=True
            p.save()

         #To retrive the records from Order_details table matching with razorpay response order id
            o=Order_details.objects.filter(order_id=response['razorpay_order_id'])
            for i in o:
                i.payment_status='Paid'
                i.save()


                c=Cart.objects.filter(user=usr)  #filter all records matching with particular user
                c.delete()

        except:
            pass

    return render(request,'payment_status.html',{'status':status})

@login_required
def order_view(request):
    u=request.user
    o=Order_details.objects.filter(user=u)
    context={'order':o}
    return render(request,'orderview.html',context)
