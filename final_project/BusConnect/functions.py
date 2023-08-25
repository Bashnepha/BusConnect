from django.conf import settings
from .models import Bus,Schedule
from twilio.rest import Client 
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
    
    
    
    
    
    