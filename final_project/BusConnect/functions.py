from django.conf import settings
from .models import Bus,Schedule
from twilio.rest import Client 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import uuid
import requests
import json
from .models import Payment
from django.core.mail import send_mail

from django.conf import settings
import re
from django.http import HttpResponse,  JsonResponse

import uuid


from django.core.mail import send_mail
from django.conf import settings

def send(subject, message, recipient_list):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,  # Set the sender email address here
        recipient_list=[recipient_list]
    )


    

import random
def send_sms(to_phone_number, message):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_phone_number = settings.TWILIO_PHONE_NUMBER

    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=message,
            from_=from_phone_number,
            to=to_phone_number
        )
        return True, message.sid
    except Exception as e:
        return False, str(e)
    
    
    
    
    
#fuction that return available bus

def get_available_bus(route, date):
    # Step I: Get all buses operating in the destination city for the given route
    buses_in_destination = Bus.objects.filter(operating_city=route.destination)

    # Step II: Create an empty list to store buses without schedules on the specified date
    buses_without_schedule = []

    # Step III: Loop through the buses in the destination city
    for bus in buses_in_destination:
        # Step IV: Check if there is no schedule for the given date, route, and bus
        if not Schedule.objects.filter(date=date, route=route, bus=bus).exists():
            # Step V: Add the bus to the list of buses without schedules
            buses_without_schedule.append(bus)
            
    

        
        # Step VI: Randomize the list of buses without schedules
    if buses_without_schedule:
        random.shuffle(buses_without_schedule)
        found = random.choices(list(buses_without_schedule))
        return found[0]
        
        
    return None
        

   
    # If no bus is found without a schedule on the specified date, return None
    

    
    
    
    
def generate_transaction_reference():
    # Generate a unique transaction reference using UUID
    transaction_ref = str(uuid.uuid4()).replace('-', '')[:12]
    return transaction_ref






# Regular expression pattern to check for special characters
SPECIAL_CHAR_PATTERN = r'[!@#-$%^&*(),.''?"":{}|<>]'


email_from=settings.EMAIL_HOST_USER



def verify_payment(tx_ref):
    user = request.user

    if not tx_ref:
        return JsonResponse({'message': 'Transaction ID is missing'}, status=404)
    
    if re.search(SPECIAL_CHAR_PATTERN, tx_ref):
            return JsonResponse({'message': 'Transaction ID contains special characters'}, status=400)
    
    try:
        payment = Payment.objects.get(user=user, tx_ref=tx_ref)
        if payment.payment_status == 'successful':
            return HttpResponse('Payment already verified')

    except Payment.DoesNotExist:
        return HttpResponse('There is no payment with such details. Please check the ID and reference')
        
    
    verify_url = f'https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}'
    headers = {
        'Authorization': f'Bearer {settings.FLUTERWAVE_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.get(verify_url, headers=headers)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        data = response.json()
        payment.status = data['data']['status'] 
        payment.amount = data['data']['amount']
        payment.save()
        return JsonResponse({'message': 'Payment verified successfully'}, status=200)

    except requests.RequestException as e:
        error_message = f'Failed to verify payment: {str(e)}'
        print(error_message)
        return JsonResponse({'message': error_message}, status=500)







@csrf_exempt
def hook(request):
    if request.method=='POST':

        # Retrieve the secret hash from environment variables
        secret_hash = settings.FLUTTERWAVE_WEBHOOK_SECRET_HASH

        # Verify that the request is from Flutterwave
        verif_hash = request.headers.get('verif-hash')
        if not verif_hash or verif_hash != secret_hash:
            return HttpResponse(status=403)

        # Retrieve the data from the webhook request
        data = json.loads(request.body)
       

        # Check that the data is from Flutterwave
        if data.get('event') != 'charge.completed':
            return HttpResponse(status=400)

        # Check that the status of the transaction was not successful before
        tx_ref = data['data']['tx_ref']
        payment= Payment.objects.filter(tx_ref=tx_ref).first()
        if not payment:
            return HttpResponse(status=404)
        
        if payment.payment_status=='successful':
            return HttpResponse(status=200)

    
        # Use the transaction details to re-fetch payment information using API
        url =  f'https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}'
        headers = {'Authorization': f'Bearer {settings.FLUTERWAVE_SECRET_KEY}'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            payment_data = response.json()['data']
           

            # Update the payment status in your database
            payment.payment_status = payment_data['status']
            payment.amount = payment_data['amount']
            payment.save()

        except requests.exceptions.RequestException as e:
            # Handle API request exception
            print(f"API request error: {str(e)}")
            return HttpResponse(status=500)

        except (KeyError, ValueError) as e:
            # Handle JSON parsing or data extraction error
            print(f"JSON parsing or data extraction error: {str(e)}")
            return HttpResponse(status=500)

        return HttpResponse(status=200)

    else:
        return HttpResponse('webhook only accept post reques')

