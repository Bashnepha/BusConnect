from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from .forms import  MyUserCreationForm, LoginForm,ArticleForm, Search_routeForm,TripForm,UserProfileForm,ComplainForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import Http404,HttpResponse,HttpResponseRedirect
from datetime import datetime,timedelta,timezone
from django.db import transaction
from .models import Route,Article,HomepageText,Faqs, OurService,PopulerRoute,Schedule,Bus,UserProfile,Complain,Payment
from django.shortcuts import render, HttpResponse
from .forms import TripForm
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from .functions import send_sms, get_available_bus,generate_transaction_reference,verify_payment
from django.contrib import messages
import requests
import re
import datetime




@login_required(login_url='login')
def complain(request):
    if request.method == 'POST':
        form = ComplainForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            return redirect('complain')
    else:
        form = ComplainForm()
        complain= Complain.objects.filter(user=request.user)
        return render(request, 'BusConnect/complain.html', {'form': form,'complain':complain})


login_required
def userprofile(request):
    user = request.user
    profile= UserProfile.objects.filter(user=user).first()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('userprofile')
        pass
        
    else:
        form = UserProfileForm()
        return render(request, 'BusConnect/userprofile.html', {'profile': profile,'form':form})




def payment(request):
    num_seats = request.session.get('num_seats', 0)
    schedule_id = request.session.get('schedule_id')

    if num_seats <= 0 or not schedule_id:
        return HttpResponse('either num_seat or schedule id are missing ')
    
    # Retrieve the schedule details  based on the schedule ID
    schedule = get_object_or_404(Schedule, id=schedule_id)
    booking_cost = schedule.route.cost * num_seats
    available_seats=schedule.get_available_seats()
    
    if available_seats < 1 or available_seats < num_seats:
        return HttpResponse('we are sorry there is no available room for number of seats you typed')
        

    if request.method == 'POST':
        user = request.user
        transaction_reference = generate_transaction_reference()
        currency = 'NGN'  # Assuming the currency is NGN
        amount = booking_cost
        customer_email= user.email
        contact=UserProfile.objects.filter(user=user).first()
        
        response = requests.post('https://api.flutterwave.com/v3/payments', headers={
        'Authorization': f'Bearer {settings.FLUTERWAVE_SECRET_KEY}',  
        }, 

        json={
        'amount': amount,
        'currency': currency,
        'tx_ref': transaction_reference,
        'redirect_url':'https://88ef-105-112-224-47.ngrok-free.app/',
        'customer': {
            'email': customer_email,
            'phonenumber':contact.phone_number,
            'name': f'{user.first_name} {user.last_name}'
        },
        'customizations': {
            'title': 'NAIBAWA BUS STATION'
        }
       })
        
        
        if response.status_code == 200:
            data = response.json()
            redirect_url = data['data']['link']

            payment = Payment.objects.create(
                user=user,
                tx_ref=transaction_reference,
                status='pending',
                payment_date=datetime.datetime.now(),
                amount=amount,
                schedule=schedule
            )
            payment.save()
            
          
            return HttpResponseRedirect(redirect_url)
        
        else:
            return HttpResponse({ 'Payment initialization failed'})
        
    
       
        
    else:
        
        # Pass the necessary data to the payment template for confirmation
        context = {
            'schedule': schedule,
            'num_seats': num_seats,
            'booking_cost': booking_cost,
        }

        return render(request, 'BusConnect/payment.html', context)
    
    
    
def payment_callback(request):
    if request.method=='GET':
        tx_ref = request.GET.get('tx_ref')
        verify_payment(tx_ref)
    else:
        return HttpResponse('invalid request method')


def book_schedule_view(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    available_seats = schedule.get_available_seats()
    
    if  available_seats < 1:
        return HttpResponse('no seat available  ')
    
    if request.method=='POST':
        num_seats =int(request.POST.get('num_seats'))
        
        # Check for the availability of seats   
        if available_seats < num_seats:
            return HttpResponse('we are sorry there is no available room for number of seats you typed')
        
        request.session['num_seats'] = num_seats
        request.session['schedule_id'] = schedule.id
        return redirect('payment')
       
       

    else: 

        # User is viewing the booking form
        context = {'schedule': schedule}
        return render(request, 'BusConnect/seat_form.html', context)







def book_trip(request):
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            time = form.cleaned_data['time']
            date = form.cleaned_data['date']

            route = get_object_or_404(Route, origin=origin, destination=destination)

            # Check for an existing schedule with the specified route, time, and date
            schedule = Schedule.objects.filter(route=route, departure_time=time, date=date).first()

            if schedule:
                # Check if the schedule has available seats
                if schedule.get_available_seats() > 0:
                    # Render the template with the available schedule
                    schedules = Schedule.objects.filter(route=route, date=date)
                    return render(request, 'BusConnect/bus_schedule.html', {'schedules': schedules})
                else:
                    return HttpResponse("No available seats for the selected schedule. Please choose another time or date.")
            else:
                # Get an available bus for the selected route and date by calling get_available_bus function defined in functions.py
                available_bus = get_available_bus(route, date)

                if not available_bus:
                    return HttpResponse("No available buses for the selected route, time, and date. Please choose another time or date.")

                # Create a new schedule using the available bus (in a transaction)
                with transaction.atomic():
                    new_schedule = Schedule.objects.create(route=route, bus=available_bus, date=date, departure_time=time)
                    new_schedule.save()

                # Render the template with the new schedule
                schedules = Schedule.objects.filter(route=route, date__gte=date)
                return render(request, 'BusConnect/bus_schedule.html', {'schedules': schedules})

    else:
        form = TripForm()

    context = {'form': form}
    return render(request, 'BusConnect/book_trip.html', context)












def homepage(request):
    homepage_text=HomepageText.objects.first()
    faqs = Faqs.objects.all()
    services = OurService.objects.all()
    populer_routes=PopulerRoute.objects.all()
    return render(request, 'BusConnect/homepage.html',
                  {'homepage_text':homepage_text,
                   'faqs':faqs,
                   'services':services,
                   'populer_routes':populer_routes
                   })






def signup(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            first_name  = form.cleaned_data['first_name']
            last_name  = form.cleaned_data['last_name']
            user = User.objects.create_user(username,email,password)
            user.first_name=first_name
            user.last_name=last_name
            user.save()
            return  redirect('login')
        
            
    else:
      form = MyUserCreationForm()
    return render(request, 'BusConnect/signup.html', {'form': form})








def login_view(request):
    # request.user.is_authenticated:
       # return HttpResponse('alrady loggedin!')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None :
                login(request, user)
                
            if user.is_superuser:
                return render(request,'BusConnect/admin_dashbord.html')
            else:
                return redirect('userprofile')
        
        else:
            error_message ='invalid login credentials'
         
    else:
        form = LoginForm()
        error_message =  ''
    return render(request, 'BusConnect/login.html', {'form': form,'error_message':error_message})




@login_required(login_url='login')
def admin_dashbord(request):
    return render(request, 'BusConnect/admin_dashbord.html')



def customer_dashbord(request):
    return render(request, 'BusConnect/customer_dashbord.html')





   

def buses_schedules(request):
    current_date= datetime.datetime.now().date()
    current_time= datetime.datetime.now().time()
    schedules= Schedule.objects.filter(date=current_date, departure_time__time__gte=current_time)
    if schedules:
        context= {'schedules':schedules}
        return render(request, 'BusConnect/bus_schedule.html',context)
    else:
        return HttpResponse('we are sorry no shedule for now ')






def available_routes(request):
    routes = Route.objects.all()
    return render(request, 'BusConnect/available_routes.html', {'routes': routes})
   
  
        
        




@login_required(login_url='login')
def add_article(request):
    
    if not request.user.is_superuser:
        raise Http404("You are not authorized to add articles.")
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('article_list')
    else:
        form = ArticleForm()
    return render(request, 'BusConnect/add_article.html', {'form': form})




@login_required(login_url='login')
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if not request.user.is_superuser and request.user != article.author:
        raise Http404("You are not authorized to delete this article.")
    
    if request.method == 'POST':
        article.delete()
        return redirect('article_list')
    return render(request, 'BusConnect/delete_article.html', {'article': article})





@login_required(login_url='login')
def edit_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if not request.user.is_superuser and request.user != article.author:
        raise Http404("You are not authorized to edit this article.")
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('article_list')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'BusConnect/edit_article.html', {'form': form})




def article_list(request):
    articles = Article.objects.all()   
    return render(request, 'BusConnect/article_list.html', {'articles': articles})




def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'BusConnect/article_detail.html', {'article': article})

def search_route(request):
    if request.method=='POST':
        form = Search_routeForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination= form.cleaned_data['destination']
            

            routes= Route.objects.filter(destination__city = destination,origin__city = origin ).all()
            #display found routes based on user input, by re using available_routes.html template, to display the found routes
            if  routes:
                return render(request, 'BusConnect/available_routes.html',{'routes':routes})
            
              
            else:
              error_massage = f'we where unable to find route that its origin is {origin} and destination is {destination}, please review you data.'
    else:
        error_massage = ''
        form=  Search_routeForm()
    return render(request,'BusConnect/serch_route.html',{'form':form,'error_massage':error_massage} )
        
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
        
        
   

def email(request):
    if request.method=='POST':
        subject=request.POST.get('subject')
        recipient=request.POST.get('recipient')
        message=request.POST.get('message')
        email_from=settings.EMAIL_HOST_USER
        send_mail(subject,message,email_from,recipient_list=[recipient])
        
    return render(request, 'BusConnect/email.html')
def sms(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        message = request.POST.get('message')

        success, sid = send_sms(phone_number, message)

        if success:
            # SMS sent successfully
            return HttpResponse('SMS sent successfully')
        else:
            # Failed to send SMS
            return HttpResponse('Failed to send SMS')

    return render(request, 'BusConnect/send_sms_form.html')
