from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarMake, CarModel, CarDealer, DealerReview
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if (request.method == 'GET'):
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact_us(request):
    context = {}
    if (request.method == 'GET'):
        return render(request, 'djangoapp/contact_us.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if (request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            #If user exists
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request, 'djangoapp/index.html', context)
        

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if (request.method == "GET"):
        return render(request, 'djangoapp/registration.html', context)
    elif (request.method == "POST"):
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password = request.POST['psw']
        is_exist = False
        try:
            User.objects.get(username=username)
            is_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not is_exist:
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, password=password)
            user.save()
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, "djangoapp/registration.html", context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = 'https://8118a41b.au-syd.apigw.appdomain.cloud/backend-process/api/dealership'
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Put dealerships into context
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
# ...
    context = {}
    if (request.method == "GET"):
        url = 'https://8118a41b.au-syd.apigw.appdomain.cloud/backend-process/api/review'
        review_list = get_dealer_reviews_from_cf(url, dealer_id)
        context["review_list"] = review_list
        context["dealer_id"] = dealer_id
        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
# ...
    context = {}
    post_url = 'https://8118a41b.au-syd.apigw.appdomain.cloud/backend-process/api/review'
    if (request.user.is_authenticated):
        if (request.method == "GET"):
            cars = CarModel.objects.filter(dealer_id=dealer_id)
            context["cars"] = cars
            context["dealer_id"] = dealer_id
            return render(request, 'djangoapp/add_review.html', context)
        elif (request.method == "POST"):    
            review = {}
            review["time"] = datetime.utcnow().isoformat()
            review["dealership"] = dealer_id
            review["review"] = request.POST["content"]
            review["name"] = request.POST["reviewername"]
            review["purchase"] = request.POST["purchasecheck"]
            review["another"] = "field"
            review["purchase_date"] = datetime.utcnow().strftime("%Y")
            car_purchased = get_object_or_404(CarModel, pk=request.POST["car"])
            review["car_make"] = car_purchased.car_make.name
            review["car_model"] = car_purchased.name
            review["car_year"] = car_purchased.year

            json_payload = {}
            json_payload["review"] = review
            response = post_request(post_url, json_payload, dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)