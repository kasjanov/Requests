# NASA API key: xXm6vYK3kpj7y1CFeGZyf1ZvMngLnaDbt29q6nFL
import datetime
import requests

from PIL import Image
from PIL import Image
from urllib.request import urlopen
from pprint import pprint

date_NASA = datetime.datetime.now().date()
city = 'Moscow Sakhalinskaya street'
my_headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/92.0.4515.131 Safari/537.36",
              'Accept': '*/*'}

url_openstreetmap = 'https://nominatim.openstreetmap.org/search'
my_params_openstreetmap = {'q': city, 'format': 'json', 'limit': 1}

response_openstreetmap = requests.get(url_openstreetmap, params=my_params_openstreetmap, headers=my_headers)
j_data_openstreetmap = response_openstreetmap.json()[0]

city_coordinates = {'Name': j_data_openstreetmap.get('display_name'),
                    'Latitude': j_data_openstreetmap.get('lat'),
                    'Longitude': j_data_openstreetmap.get('lon')}


url_NASA = 'https://api.nasa.gov/planetary/earth/assets'
api_key_NASA = 'xXm6vYK3kpj7y1CFeGZyf1ZvMngLnaDbt29q6nFL'
my_params_NASA = {'lat': city_coordinates.get('Latitude'),
                  'lon': city_coordinates.get('Longitude'),
                  'date': date_NASA,
                  'dim': 0.75,
                  'api_key': api_key_NASA}

response_NASA = requests.get(url_NASA, params=my_params_NASA, headers=my_headers)

while not response_NASA.ok:
    date_NASA -= datetime.timedelta(days=1)
    my_params_NASA['date'] = date_NASA
    response_NASA = requests.get(url_NASA, params=my_params_NASA, headers=my_headers)

j_data_NASA = response_NASA.json()

photo_NASA = Image.open(urlopen(j_data_NASA.get('url')))
photo_NASA.show()
photo_NASA_name = j_data_openstreetmap.get('display_name') + ' ' + \
                  '_'.join('_'.join(j_data_NASA.get('date').split('-')).split(':'))[:10]+'.png'
photo_NASA.save(photo_NASA_name)

print(j_data_NASA.get('url'))
print(f'{j_data_openstreetmap.get("display_name")} широта {j_data_openstreetmap.get("lat")} '
      f'долгота {j_data_openstreetmap.get("lon")}')

