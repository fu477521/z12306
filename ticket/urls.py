
from django.urls import path
from ticket import views

app_name = 'ticket'
urlpatterns = [
    path('', views.Index, name='home'),
    path('ticket/', views.Ticket, name='ticket'),
    path('send_mes/', views.Send_messsage, name='send_mes'),
]