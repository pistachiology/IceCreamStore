from django.shortcuts import render
from django.shortcuts import render_to_response, redirect, get_object_or_404, HttpResponseRedirect
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import connection, IntegrityError
from django.contrib import messages
from .models import *
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError
from django.core import serializers
from django.http import JsonResponse, HttpResponse
import json
import sys

# Create your views here.
class index(View):
    template_name = "store/index.html"
    def get(self, request):
        #obj, created = User.objects.get_or_create(username="admin", password="1234", isAdmin=True)
        #print created
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/store/product")  

        history = Tracking.objects.filter(user=request.user, current_state=4).count()
        track = Tracking.objects.filter(user=request.user).exclude(current_state=4).count()
        product = Product.objects.all().count()
        cart = Cart.objects.filter(user=request.user).count()

        return render(request, self.template_name, {'history': history, 'track': track, 'cart': cart, 'product': product})


class login_view(View):
    template_name = "store/login.html"
    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        next_page = ""
        if user is not None:
            login(request, user)
            if "next" not in request.GET:
                next_page = "/store/"
            else:
                next_page = request.GET['next']
            return HttpResponseRedirect(next_page)
        return render(request, self.template_name, {'err_message': 'Invalid username/password'})

class register(View):
    template_name = "store/register.html"

    # @method_decorator(login_required)
    def get(self, request):
        #if not 'is_logged_in' in request.session or not request.session['is_logged_in']:
        #    return redirect("/store/login")
        return render(request, self.template_name, {})
      
    def post(self, request):
        response = {}
        for key in request.POST.keys():
            response[key] = request.POST.get(key, '')
        if CustomUser.objects.filter(username=response['username']).exists():
            messages.error(request, 'Username already exists', extra_tags='alert-danger')
        if response['username'] == "":
            messages.error(request, 'Username required', extra_tags='alert-danger')
        if response['password'] != response['repassword']:
            messages.error(request, 'Password not matched', extra_tags='alert-danger')
        if response['password'] == "":
            messages.error(request, 'Password required', extra_tags='alert-danger')
        if response['first_name'] == "":
            messages.error(request, 'Firstname can\'t be empty', extra_tags='alert-danger')
            response['err_message'] = "Null value at First Name"
        if response['last_name'] == "":
            messages.error(request, 'Lastname can\'t be empty', extra_tags='alert-danger')
        if response['email'] == "":
            messages.error(request, 'E-mail can\'t be empty', extra_tags='alert-danger')
        if response['address'] == "":
            messages.error(request, 'Address can\'t be empty', extra_tags='alert-danger')
        if response['tel'] == "":
            messages.error(request, 'Telephone can\'t be empty', extra_tags='alert-danger')
        if not list(messages.get_messages(request)):
            try:
                newUser = CustomUser(username=response['username'],
                               is_superuser=0,
                               first_name=response['first_name'],
                               last_name=response['last_name'],
                               email=response['email'],
                               address=response['address'],
                               tel=response['tel'],
                               company=response['company'])
                newUser.set_password(response['password'])
                newUser.save()
                messages.success(request, 'Register Complete', extra_tags='alert-success')
                return redirect('/store/login')
            except IntegrityError as e:
                response['err_message'] = "Username already exists(2)"
                response["password"] = ""
                response["repassword"] = ""
                return render(request, self.template_name, response)
        else:
            response["password"] = ""
            response["repassword"] = ""
            return render(request, self.template_name, response)

class all_product(View):
    template_name = "store/all_product.html"
    def get(self, request):
        response = {}
        products = Product.objects.all()
        response['products'] = products
        return render(request, self.template_name, response)

    @method_decorator(login_required)
    def post(self, request):
    	try:
            product_id = int(request.POST['product_id'])
            amount = int(request.POST['amount'])
            product = Product.objects.get(id=product_id)
            current_amount = product.amount
            if amount < 0 or amount > current_amount:
                return JsonResponse({"status": "invalid amount"})
            Cart(user=CustomUser.objects.get(id=request.user.id), product=product, qty=amount).add_or_update()
        except ValueError, MultiValueDictKeyError:
            raise Http404("product doesn't exists")
        return JsonResponse({"status": "success"})

class popular_product(View):
    template_name = "store/popular_product.html"
    def get(self, request):
        response = {}
        products = Product.objects.all().order_by('-score')
        response['products'] = products
        return render(request, self.template_name, response)

    @method_decorator(login_required)
    def post(self, request):
    	try:
            product_id = int(request.POST['product_id'])
            amount = int(request.POST['amount'])
            product = Product.objects.get(id=product_id)
            current_amount = product.amount
            if amount < 0 or amount > current_amount:
                return JsonResponse({"status": "invalid amount"})
            Cart(user=CustomUser.objects.get(id=request.user.id), product=product, qty=amount).add_or_update()
        except ValueError, MultiValueDictKeyError:
            raise Http404("product doesn't exists")
        return JsonResponse({"status": "success"})

class product(View):
    template_name = "store/product.html"

    def get(self, request, product_id):
        product = get_object_or_404(Product,pk=product_id)
        product = json.loads(serializers.serialize('json', [product])[1:-1])
        return JsonResponse(product)

    def post(self, request, product_id):
        pass

class history(View):
    template_name = "store/history.html"
    @method_decorator(login_required)
    def get(self, request):
        history = Tracking.objects.filter(user=request.user, current_state=4)
        return render(request, self.template_name, {"history":history})

class all_track(View):
    template_name = "store/all_track.html"
    @method_decorator(login_required)
    def get(self, request):
        tracks = Tracking.objects.exclude(current_state=4).filter(user=request.user)
        return render(request, self.template_name, {"tracks": tracks})

class track(View):
    template_name = "store/track.html"

    def get(self, request, track_id):
        pass

class profile(View):
    template_name = "store/profile.html"
     
    @method_decorator(login_required)
    def get(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        return render(request, self.template_name, {'user': user})

    @method_decorator(login_required)
    def post(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.address = request.POST.get('address', '')
        user.tel = request.POST.get('tel', '')
        authen = authenticate(username=user.username, password=request.POST.get('password', ''))
        if authen is not None:
            user.save()
            messages.success(request, "Successfully edited profile.", extra_tags="alert-info")
            return render(request, self.template_name)
        messages.error(request, "Invalid password", extra_tags="alert-danger")
        return render(request, self.template_name, {'user': user})


class contact_us(View):
    template_name = "store/contact_us.html"

    def get(self, request):
        return render(request, self.template_name, {
            'email':'kitchaphan.s@ku.th',
            'tel':'081-4623115',
            'address':'chapterone@kaset',
        })


class cart(View):
    template_name = "store/cart.html"

    @method_decorator(login_required)
    def get(self, request):
        user_cart = Cart.objects.filter(user=request.user)
        return render(request, self.template_name, {'user_cart': user_cart})

class delete_cart(View):
    def get(self, request, cart_id):
        try:
            x = Cart.objects.get(id=cart_id)
            x.delete()
        except Cart.DoesNotExist:
            messages.error(request, "Cart does not exist.", extra_tags="alert-danger")
        return HttpResponseRedirect("/store/cart/")

class logout_view(View):
    template_name = "store/logout.html"
    
    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/store/")

    def post(self, request):
        logout(request)
        return HttpResponseRedirect("/store/")

class purchase(View):
    template_name = "store/cart.html"
    @method_decorator(login_required)
    def post(self, request):
        if request.user.purchase() :
            messages.success(request, "Purchase success.", extra_tags="alert-info")
        else:
            messages.error(request, "Purchase failed.", extra_tags="alert-danger")
        return HttpResponseRedirect("/store/cart/")  
        
class clear_cart(View):
    template_name = "store/cart.html"
    @method_decorator(login_required) 
    def get(self, request):
        request.user.user_cart.clear()
        return HttpResponseRedirect("/store/cart/")  

class user_vote(View):
    template_name = "store/vote.html" # not sure
    
    def get(self, request, product_id):
        prod = Product.objects.get(id=product_id)
        back_url = request.GET.get("back_url", "/store/")
        return render(request, self.template_name, {"product": prod, "back_url": back_url})

    def post(self, request, product_id):
        vote = VoteProduct(user=request.user,product=Product.objects.get(id=product_id),score=float(request.POST.get('score',0)))
        vote.user_vote_or_update_score()
        messages.success(request, "Vote successfully", extra_tags="alert-info")
        back_url = request.GET.get("back_url", "/store/")
        return HttpResponseRedirect(back_url)
