from django.shortcuts import render,redirect
from shop.models import Category
from shop.models import Product
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# Create your views here.

def categories(request):
    c=Category.objects.all()
    context={'cat':c}
    return render(request,'categories.html',context)

@login_required
def products(request,p):             #here p receives the category id
    c=Category.objects.get(id=p)        #reads a particular category object using id
    p=Product.objects.filter(category=c)    #reads all products under a particular category object
    context={'cat':c,'pro':p}
    return render(request,'products.html',context)

@login_required
def details(request,p):
    pro=Product.objects.get(id=p)
    context={'product':pro}
    return render(request,'details.html',context)

def register(request):
    if(request.method=='POST'):
        u=request.POST['u']
        p = request.POST['p']
        cp = request.POST['cp']
        fn = request.POST['fn']
        ln = request.POST['ln']
        e = request.POST['e']

        if(p==cp):
            u=User.objects.create_user(username=u,password=p,first_name=fn,last_name=ln,email=e)
            u.save()
            return redirect('shop:categories')

        else:
            return HttpResponse('Password are not same')


    return render(request,'register.html')


def user_login(request):
    if(request.method=='POST'):
        u=request.POST['u']
        p=request.POST['p']

        user=authenticate(username=u,password=p)
        if user:
            login(request,user)
            return redirect('shop:categories')
        else:
            return HttpResponse('Invalid Credentials')


    return render(request,'login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('shop:login')

def add_categories(request):
    if(request.method=='POST'):
        n=request.POST['n']
        i=request.FILES['i']
        d=request.POST['d']

        c=Category.objects.create(name=n,image=i,description=d)
        c.save()
        return redirect('shop:categories')
    return render(request,'addcat.html')

def add_products(request):
    if(request.method=='POST'):
        n=request.POST['n']
        i = request.FILES['i']
        d = request.POST['d']
        s = request.POST['s']
        p = request.POST['p']
        c=request.POST['c']

        cat=Category.objects.get(name=c)

        p=Product.objects.create(name=n,image=i,description=d,stock=s,price=p,category=cat)
        p.save()
        return redirect('shop:categories')

    return render(request,'addpro.html')

def add_stock(request,p):
    product=Product.objects.get(id=p)
    if(request.method=='POST'):
        product.stock=request.POST['s']
        product.save()
        return redirect('shop:details',p)    #while calling to the details page, adds the product id value i,e,'p'

    context={'pro':product}

    return render(request,'addstock.html',context)