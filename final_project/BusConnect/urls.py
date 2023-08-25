from django.urls import path
from . import views
urlpatterns = [
    path('',views.homepage, name='homepage'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('user/profile/', views.userprofile, name='userprofile'),
    path('admin_dashbord/', views.admin_dashbord, name='admin_dashbord'),
    path('articles', views.article_list, name='article_list'),
    path('add/', views.add_article, name='add_article'),
    path('edit/<int:article_id>/', views.edit_article, name='edit_article'),
    path('delete/<int:article_id>/', views.delete_article, name='delete_article'),
    path('detail/<int:article_id>/', views.article_detail, name='article_detail'),
    path('available_routes/', views.available_routes, name='available_routes'),
    path('routes/search/', views.search_route, name='search_route'),
    path('buses_schedules/', views.buses_schedules, name='buses_schedules'),
    path('trip/book', views.book_trip, name='book_trip'),
    path('book-schedule/<int:schedule_id>/', views.book_schedule_view, name='book_schedule'),
    path('payment', views.payment, name='payment'),
    path('sms', views.sms, name='sms'),
    path('email', views.email, name='email'),
    path('complain', views.complain, name='complain'),
    
    
    
    
]
