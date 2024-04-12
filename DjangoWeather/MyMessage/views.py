
from django.http import HttpResponse

def home(request):
    # This is the dummy view function 
    return HttpResponse('Welcome to DjangoWeather!')

import requests
from django.http import JsonResponse
from django.conf import settings  

def weather_by_city_name(request, city_name):
    api_key = settings.ACCUWEATHER_API_KEY

    # getting the location key from accuweather
    location_url = 'http://dataservice.accuweather.com/locations/v1/cities/search'
    location_params = {'apikey': api_key, 'q': city_name}
    location_response = requests.get(location_url, params=location_params)

    if location_response.status_code != 200:
        return JsonResponse({'error': 'Failed to fetch location key'}, status=location_response.status_code)

    locations = location_response.json()
    if not locations:
        return JsonResponse({'error': 'City not found'}, status=404)


    # getting the 5-day weather info based on the location key
    location_key = locations[0]['Key']
    forecast_url = f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}'
    forecast_params = {'apikey': api_key, 'metric': True}  
    forecast_response = requests.get(forecast_url, params=forecast_params)

    if forecast_response.status_code != 200:
        return JsonResponse({'error': 'Failed to fetch forecast data'}, status=forecast_response.status_code)

    forecast_data = forecast_response.json()
    forecasts = []

    for daily_forecast in forecast_data.get('DailyForecasts', []):
        day_icon_number = str(daily_forecast['Day']['Icon']).zfill(2)
        night_icon_number = str(daily_forecast['Night']['Icon']).zfill(2)

        forecasts.append({
            'date': daily_forecast.get('Date', ''),
            'minTemp': daily_forecast.get('Temperature', {}).get('Minimum', {}).get('Value', 'N/A'),
            'maxTemp': daily_forecast.get('Temperature', {}).get('Maximum', {}).get('Value', 'N/A'),
            'dayPhase': daily_forecast.get('Day', {}).get('IconPhrase', 'N/A'),
            'nightPhase': daily_forecast.get('Night', {}).get('IconPhrase', 'N/A'),
            'dayIconUrl': f"https://developer.accuweather.com/sites/default/files/{day_icon_number}-s.png",
            'nightIconUrl': f"https://developer.accuweather.com/sites/default/files/{night_icon_number}-s.png"
        })
    

    # getting the 12-hour weather info base don the location key
    hourly_forecast_url = f'http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{location_key}'
    hourly_forecast_response = requests.get(hourly_forecast_url, params=forecast_params)

    if hourly_forecast_response.status_code != 200:
        return JsonResponse({'error': 'Failed to fetch hourly forecast data'}, status=hourly_forecast_response.status_code)

    hourly_forecast_data = hourly_forecast_response.json()
    hourly_forecasts = []  

    for forecast in hourly_forecast_data:
        
        icon_number = str(forecast.get('WeatherIcon', '')).zfill(2)
        icon_url = f"https://developer.accuweather.com/sites/default/files/{icon_number}-s.png"

        # Parse the forecast data for each hour
        hourly_forecasts.append({
            'DateTime': forecast.get('DateTime', ''),  
            'Temperature': forecast.get('Temperature', {}).get('Value', 'N/A'),  
            'PrecipitationProbability': forecast.get('PrecipitationProbability', 'N/A'),  
            'IconPhrase': forecast.get('IconPhrase', 'N/A'),  
            'IconUrl': icon_url  
        })

    # getting the image for background
    first_day_forecast = forecast_data['DailyForecasts'][0]
    current_weather = first_day_forecast.get('Day', {}).get('IconPhrase', 'Not Available')
    city_image_url = fetch_city_image(city_name, current_weather)

    return JsonResponse({'forecasts': forecasts, 'hourly_forecasts': hourly_forecasts, 'cityImageUrl': city_image_url})

def fetch_city_image (city_name, current_weather):
    unsplash_access_key = settings.UNSPLASH_API_KEY
    query = f"{city_name} {current_weather} cityscape"
    unsplash_url = f"https://api.unsplash.com/search/photos?page=1&query={query}&client_id={unsplash_access_key}"
    image_url = None

    try:
        unsplash_response = requests.get(unsplash_url)
        if unsplash_response.status_code == 200:
            unsplash_data = unsplash_response.json()
            if unsplash_data['results']:
                image_url = unsplash_data['results'][0]['urls']['regular']
    except Exception as e:
        print(f"Error fetching image: {e}")
    
    return image_url



# handler for the current city/cooridantes
def weather_by_coordinates(request):
    latitude = request.GET.get('lat')
    longitude = request.GET.get('lon')
    if not latitude or not longitude:
        return JsonResponse({'error': 'Missing latitude or longitude parameters'}, status=400)

    api_key = settings.ACCUWEATHER_API_KEY
    location_url = f'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={api_key}&q={latitude},{longitude}'

    try:
        location_response = requests.get(location_url)
        location_data = location_response.json()
        location_key = location_data['Key']
        city_name = location_data['LocalizedName']

        # Fetch the 5-day forecast
        forecast_url = f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}?apikey={api_key}&metric=true'
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()

        # Process the forecast data
        forecasts = []
        for daily_forecast in forecast_data.get('DailyForecasts', []):
            day_icon_number = str(daily_forecast['Day']['Icon']).zfill(2)
            night_icon_number = str(daily_forecast['Night']['Icon']).zfill(2)

            forecasts.append({
                'date': daily_forecast.get('Date', ''),
                'minTemp': daily_forecast.get('Temperature', {}).get('Minimum', {}).get('Value', 'N/A'),
                'maxTemp': daily_forecast.get('Temperature', {}).get('Maximum', {}).get('Value', 'N/A'),
                'dayPhase': daily_forecast.get('Day', {}).get('IconPhrase', 'N/A'),
                'nightPhase': daily_forecast.get('Night', {}).get('IconPhrase', 'N/A'),
                'dayIconUrl': f"https://developer.accuweather.com/sites/default/files/{day_icon_number}-s.png",
                'nightIconUrl': f"https://developer.accuweather.com/sites/default/files/{night_icon_number}-s.png"
            })

        # Fetch the hourly forecast 
        hourly_forecast_url = f'http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{location_key}?apikey={api_key}&metric=true'
        hourly_forecast_response = requests.get(hourly_forecast_url)
        hourly_forecast_data = hourly_forecast_response.json()

        hourly_forecasts = [{
            'DateTime': forecast['DateTime'],
            'Temperature': forecast['Temperature']['Value'],
            'PrecipitationProbability': forecast['PrecipitationProbability'],
            'IconPhrase': forecast['IconPhrase'],
            'IconUrl': f"https://developer.accuweather.com/sites/default/files/{str(forecast['WeatherIcon']).zfill(2)}-s.png"
        } for forecast in hourly_forecast_data]

        # Fetch the city image
        current_weather = forecast_data['DailyForecasts'][0]['Day']['IconPhrase']
        city_image_url = fetch_city_image(city_name, current_weather)

        return JsonResponse({
            'cityName': city_name,
            'forecasts': forecasts,
            'hourly_forecasts': hourly_forecasts,
            'cityImageUrl': city_image_url
        })

    except requests.RequestException as e:
        return JsonResponse({'error': 'Failed to communicate with AccuWeather API'}, status=500)
        