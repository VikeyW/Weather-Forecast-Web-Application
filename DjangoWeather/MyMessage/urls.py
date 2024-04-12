from django.urls import path
from . import views  


urlpatterns = [
    path('weather/<str:city_name>/', views.weather_by_city_name, name='weather_by_city_name'),
    path('weather/byCoordinates', views.weather_by_coordinates, name='weather_by_coordinates'),
]
