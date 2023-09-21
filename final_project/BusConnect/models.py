from django.db import models

# Create your models here.
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from datetime import date, time,datetime
from django.utils import timezone



class OurService(models.Model):
    service_title = models.CharField(max_length=100)
    service_description = models.TextField()
    service_icon = models.CharField(max_length=15)

    def __str__(self):
        return self.service_title
    
    


class  Faqs(models.Model):
    question=models.CharField(max_length=50)
    answer=models.TextField(max_length=1000)
    
    def __str__(self):
        return f" {self.question}"
    
    
    
    

class HomepageText(models.Model):
    our_history =   models.TextField(max_length=1000)
    our_mission = models.TextField(max_length=1000)
    our_vission = models.TextField(max_length=1000)
    
    def __str__(self):
        return f"{self.our_mission}"
    
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures',null=True)
    date_of_birth = models.TextField(max_length=500)
    phone_number = models.IntegerField(null=True)
    address = models.CharField(max_length=200)
    nationality= models.CharField(max_length=15, default='Nigeria')
    state_of_origin= models.CharField(max_length=15, null=True)
    local_government= models.CharField(max_length=15, null=True)
    address= models.CharField(max_length=40, null=True)
    nin_number=models.IntegerField(null=True)
    
    
    date_of_birth = models.DateField()

    def __str__(self):
        return self.user.username



class Station(models.Model):
    city=models.CharField(max_length=12)
    station_name= models.CharField(max_length=12)
    station_state= models.CharField(max_length=12)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['city', 'station_name'], name='unique_station')
        ]
    def __str__(self):
        return (f'{self.city}({self.station_name})')





class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    contact_number = models.CharField(max_length=20)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.user.get_full_name()








class Route(models.Model):     
    origin =models.ForeignKey(Station,on_delete=models.CASCADE,related_name='origin_city')
    destination= models.ForeignKey(Station,on_delete=models.CASCADE, related_name='depatures')
    distance = models.CharField(max_length=12)
    duration = models.CharField(max_length=12)
    route_name = models.CharField(max_length=100)
    transportation_mode = models.CharField(max_length=50)
    cost=models.IntegerField()


    def __str__(self):
        return f"Route from {self.origin} to {self.destination}"

    
    def save(self, *args, **kwargs):
        existing_route = Route.objects.filter(origin=self.origin, destination=self.destination).first()
        if existing_route:
            if self.pk != existing_route.pk:
                raise ValidationError("A route with the same origin and destination already exists.")
        super().save(*args, **kwargs)
        
        

    
class PopulerRoute(models.Model):
    route = models.ForeignKey(Route,on_delete=models.CASCADE)
    


    

class Bus(models.Model):
    bus_number = models.CharField(max_length=20, unique=True)
    driver = models.OneToOneField(Driver, on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField()
    model_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    operating_city=models.ForeignKey(Station,on_delete=models.CASCADE)
    def __str__(self):
        return f'Bus {self.bus_number} '

    

class WorkingHour (models.Model):
    time = models.TimeField(null=True)
    
    def __str__(self):
        return f'{self.time}'
    

   

   
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=50)
    tx_ref=models.CharField(max_length=30,null=True)
    schedule = models.ForeignKey('BusConnect.Schedule', on_delete=models.CASCADE,related_name='booking_payment')
    
    
    def __str__(self):
        return f"Payment {self.id}"



class Schedule(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    date = models.DateField()
    departure_time = models.ForeignKey(WorkingHour,on_delete=models.CASCADE ,default=1)

    class Meta:
        unique_together = ['bus', 'route', 'date', 'departure_time']
        
        
    def get_booked_seats(self):
        total_seats=sum(len(booking.get_seat_numbers_list() ) for booking in self.bookings.all())
        return total_seats or 0

    def get_available_seats(self):
        total_capacity = self.bus.capacity
        total_booked_seats = self.get_booked_seats()
        return total_capacity - total_booked_seats

    def get_unbooked_seats(self):
        total_capacity = self.bus.capacity
        booked_seats = set()
        for booking in self.bookings.all():
            booked_seats.update(booking.get_seat_numbers_list())
        all_seats = set(range(1, total_capacity + 1))
        unbooked_seats = list(all_seats - booked_seats)
        unbooked_seats.sort()
        return unbooked_seats
    
    
        

       
    
    def __str__(self):
        return f"{self.bus.bus_number}, {self.route}, {self.date}, {self.departure_time.time}"
    

    

        


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE,related_name='bookings')
    seat_numbers =  models.CharField(max_length=100)
    booking_date = models.DateField(null=True)
    seats_booked = models.PositiveIntegerField(default=1)
    Payment=models.OneToOneField(Payment,on_delete=models.CASCADE)
    
    
    

    def get_seat_numbers_list(self):
        return [int(seat_number) for seat_number in self.seat_numbers.split(",") if seat_number.isdigit()]
    

    
    def save(self, *args, **kwargs):
        selected_seats = self.get_seat_numbers_list()
        unbooked_seats=self.schedule.get_unbooked_seats()
        
        if len(selected_seats) < 1 :
            raise ValidationError('select vald seat numbers seperated by comma if morethan one, value must be positive and integer')
        if len(selected_seats) != self.seats_booked:
            raise ValidationError(f'you selected to book {self.seats_booked} seats, but you choose {len(selected_seats)} seats')
        
        for seat in selected_seats:
            if seat > self.schedule.bus.capacity:
                raise ValidationError(f'seat number {seat} exceded bus capacity')
            if seat < 1:
                raise ValidationError(f'seat {seat} can not be nagative')
            if seat not in unbooked_seats:
                raise ValidationError(f'seat {seat} is alrady booked')
             
        super().save(*args, **kwargs)

        
      
    def __str__(self):
        return f"Booking {self.schedule} - Seat: {self.seat_numbers}"
    

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_superuser': True})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Complain(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    subject = models.CharField(max_length=200,null=True)
    description = models.TextField(null=True)
    is_resolved = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True,null=True)



    


    
    
    
    
    





