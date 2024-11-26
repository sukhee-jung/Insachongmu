import requests
import os

from dotenv import load_dotenv

load_dotenv()

SERVICE_KEY = os.environ.get("SERVICE_KEY")

api_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

params = {
    'serviceKey': SERVICE_KEY,
    'numOfRows': '500',
    'dataType': 'JSON',
    'base_time': '0800',
    'pageNo': '1',
}

# Initialize cached_data as a dictionary
cached_data = {}

def fetch_data_from_kma(current_time_kst, category, fcst_time, nx, ny):
    global cached_data
    
    try:
        cache_key = nx + ny
        
        # Make GET request to API using params_key as the key in cached_data
        if cache_key not in cached_data:
            date_format = "YYYYMMDD"
            base_date = current_time_kst.format(date_format)
            params['base_date'] = base_date
            params['nx'] = nx
            params['ny'] = ny
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            cached_data[cache_key] = response.json()
        
        # Retrieve data from cached_data using cache_key
        data = cached_data[cache_key]

        # Extract and filter items based on category and fcst_time
        items = data['response']['body']['items']['item']
        filtered_items = [item for item in items if item['category'] == category and item['fcstTime'] == fcst_time]

        print(filtered_items[0])

        return filtered_items[0]['fcstValue']

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Something went wrong: {err}")

    return None
