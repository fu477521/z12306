
from django.urls import path
from ticket import views

app_name = 'ticket'
urlpatterns = [
    path('', views.Index, name='home'),
    path('ticket/', views.Ticket, name='ticket'),
    path('check_login/', views.Check_login, name='check_login'),
    path('login/', views.Login, name='login'),
    path('send_mes/', views.Send_messsage, name='send_mes'),
]