
from django.contrib import admin
from django.contrib.auth.admin  import  UserAdmin
from django.contrib.auth.models import  User

from django.contrib import admin
from .models import Payment, Station,  Driver, Bus, Route, Booking, UserProfile, Article,HomepageText,Faqs, OurService, PopulerRoute,Schedule,WorkingHour


# Register your models here.
class UserAdmin(UserAdmin):
    list_display =  ( 'username','first_name', 'last_name',  'email', 'is_superuser','is_active')

   
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'payment_date', 'status', 'transaction_id','schedule')



class StationAdmin(admin.ModelAdmin):
    list_display = ('id', 'city','station_name','station_state')


class FaqsAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer')
    
class PopulerRouteAdmin(admin.ModelAdmin):
    list_display=('id','route')
    

class HomepageTextAdmin(admin.ModelAdmin):
    list_display = ('id', 'our_mission', 'our_vission','our_history')



class DriverAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'license_number', 'date_of_birth', 'contact_number', 'address')



class BusAdmin(admin.ModelAdmin):
    list_display = ('id', 'bus_number', 'driver', 'capacity', 'model_type', 'is_active','operating_city')



class RouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'origin', 'destination', 'distance', 'duration', 'route_name', 'transportation_mode', 'cost')



class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'seat_numbers','booking_date','schedule')



class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'bio', 'contact_info', 'address', 'date_of_birth')



class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content', 'author', 'created_at')
    
    

class ScheduleAdmin(admin.ModelAdmin):
    list_display=('id','bus','route','date','departure_time')

class OurServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_title', 'service_description', 'service_icon',)
    



admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(OurService, OurServiceAdmin)
admin.site.register(Faqs, FaqsAdmin)
admin.site.register(HomepageText, HomepageTextAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Bus, BusAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(PopulerRoute, PopulerRouteAdmin)
admin.site.register(Schedule,ScheduleAdmin)
admin.site.register(WorkingHour)











