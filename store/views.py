from django.shortcuts import render
from django.shortcuts import render_to_response, redirect, get_object_or_404, HttpResponseRedirect
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import connection, IntegrityError
from django.contrib import messages
from .models import *
import sys

# Create your views here.
class index(View):
    template_name = "store/index.html"
    def get(self, request):
        #obj, created = User.objects.get_or_create(username="admin", password="1234", isAdmin=True)
        #print created
        return render(request, self.template_name, {})

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
        response['err_occur'] = "The following errors occur:"
        response['err_message'] = ""
        for key in request.POST.keys():
            response[key] = request.POST.get(key, '')
        if CustomUser.objects.filter(username=response['username']).exists():
            response['err_message'] = "Username already exists"
        if response['username'] == "":
            response['err_message'] = "Username is required"
        if response['password'] != response['repassword']:
            response['err_message'] = "Password not match."
        if response['password'] == "":
            response['err_message'] = "Password is required"
        if response['first_name'] == "":
            response['err_message'] = "Null value at First Name"
        if response['last_name'] == "":
            response['err_message'] = "Null value at Last Name"
        if response['email'] == "":
            response['err_message'] = "Null value at E-mail"
        if response['address'] == "":
            response['err_message'] = "Null value at Address"
        if response['tel'] == "":
            response['err_message'] = "Null value at Tel."
        if response['err_message'] == "":
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
                messages.success(request, 'Register Complete', extra_tags='register_success')
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

class product(View):
    template_name = "store/product.html"

    def get(self, request, product_id):
        pass

    def post(self, request, product_id):
        pass

class history(View):
    template_name = "store/history.html"

    def get(self, request):
        return render(request, self.template_name, {})

class all_track(View):
    template_name = "store/all_track.html"

    def get(self, request):
        return render(request, self.template_name, {})

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
            messages.success(request, "Successfully edited profile.")
            return render(request, self.template_name)
        messages.error(request, "Invalid password")
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

    def get(self, request):
        return render(request, self.template_name, {})
