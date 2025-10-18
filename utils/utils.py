import math
import requests
import jwt
from datetime import datetime, timedelta
import time

SECRET_KEY = ''


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


def get_city_by_ip(ip_address):
    url = f"http://ip-api.com/json/{ip_address}"
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'success':
        return {
            "ip": data['query'],
            "city": data['city'],
            "region": data['regionName'],
            "country": data['country'],
            "lat": data['lat'],
            "lon": data['lon'],
            "timezone": data['timezone']
        }
    else:
        return False


def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=9999)  # Токен действителен 1 час
    }
    # Создаем токен
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload['exp'] <= time.time():
            return {"error": 'Token has expired'}
        else:
            return payload
    except jwt.ExpiredSignatureError:
        return {"error": 'Token has expired'}
    except jwt.InvalidTokenError:
        return {"error": 'Invalid token'}
