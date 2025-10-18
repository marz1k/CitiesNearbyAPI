from flask import request, jsonify, Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import asyncio
from utils.utils import get_city_by_ip, verify_token, SECRET_KEY
from loader import db

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["10 per minute"]
)


def get_jwt_token():
    auth_token = request.headers.get('X-Token')
    if auth_token:
        return auth_token
    return None


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-Token')
        token = token.split(" ")[-1]
        if 'error' not in verify_token(token):
            return f(*args, **kwargs)
        else:
            return jsonify(verify_token(token)), 401

    return decorated_function


@app.route('/getCitiesByName', methods=['GET'])
@token_required
@limiter.limit("60 per minute")
def get_cities_by_name():
    """
    Name - City name. Center of the searching radius.
    Radius - radius in km. Default 30. Min 1 / Max 100
    Limit - max cities to return. Default 10. Min 1 / Max 100
    :return:
    """
    name = request.args.get('name')
    radius = request.args.get('radius')
    limit = request.args.get('limit')

    if not name:
        return jsonify({"error": "Missing 'name' parameter"}), 400

    query_args = {
        'city': name
    }
    try:
        if radius:
            if 1 <= int(radius) <= 100:
                query_args['radius'] = float(radius)
            else:
                return jsonify({'error': "Radius. Min - 1km, Max - 100km"}), 400

        if limit:
            if 1 <= int(limit) <= 100:
                query_args['limit'] = int(limit)
            else:
                return jsonify({'error': "Limit. Min - 1, Max - 100"}), 400

        result = asyncio.run(db.get_cities_by_name(**query_args))

        if result is False:
            return jsonify({"error": f"City '{name}' not found"}), 404
        else:
            return jsonify(result), 200

    except ValueError:
        return jsonify({'error': "radius or limit must be integer"}), 400


@app.route('/getCitiesByCoord', methods=['GET'])
@token_required
@limiter.limit("60 per minute")
def get_cities_by_coordinates():
    """
    Latitude - FLOAT.
    Longitude - FLOAT.
    Radius - radius in km. Default 30. Min 1 / Max 100
    Limit - max cities to return. Default 10. Min 1 / Max 100
    :return:
    """
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    radius = request.args.get('radius')
    limit = request.args.get('limit')

    if not lat or not lng:
        return jsonify({"error": "Missing 'lat' or 'lng' parameters."}), 400

    try:
        query_args = {
            'lat': float(lat),
            'lng': float(lng)
        }
    except ValueError:
        return jsonify({"error": "'lat' and 'lng' parameters must be float numbers."}), 400

    try:
        if radius:
            if 1 <= int(radius) <= 100:
                query_args['radius'] = float(radius)
            else:
                return jsonify({'error': "Radius. Min - 1km, Max - 100km"}), 400

        if limit:
            if 1 <= int(limit) <= 100:
                query_args['limit'] = int(limit)
            else:
                return jsonify({'error': "Limit. Min - 1, Max - 100"}), 400

        result = asyncio.run(db.get_cities_by_coordinates(**query_args))

        if result is False:
            return jsonify({"error": f"nothing has been found"}), 404
        else:
            return jsonify(result), 200

    except ValueError:
        return jsonify({'error': "radius or limit must be integer"}), 400


@app.route('/getCitiesByIP', methods=['GET'])
@token_required
@limiter.limit("60 per minute")
def get_cities_by_ip():
    """
    IP - str.
    Radius - radius in km. Default 30. Min 1 / Max 100
    Limit - max cities to return. Default 10. Min 1 / Max 100
    :return:
    """
    ip = request.args.get("ip")
    radius = request.args.get('radius')
    limit = request.args.get('limit')

    if not ip:
        return jsonify({"error": "Missing 'ip' parameter."}), 400
    city = get_city_by_ip(ip)
    if not city:
        return {"error": "Invalid IP address or service limit reached"}

    query_args = {
        'city': get_city_by_ip(ip)['city']
    }
    try:
        if radius:
            if 1 <= int(radius) <= 100:
                query_args['radius'] = float(radius)
            else:
                return jsonify({'error': "Radius. Min - 1km, Max - 100km"}), 400

        if limit:
            if 1 <= int(limit) <= 100:
                query_args['limit'] = int(limit)
            else:
                return jsonify({'error': "Limit. Min - 1, Max - 100"}), 400

        result = asyncio.run(db.get_cities_by_name(**query_args))

        if result is False:
            return jsonify({"error": f"City '{city}' not found"}), 404
        else:
            return jsonify(result), 200

    except ValueError:
        return jsonify({'error': "radius or limit must be integer"}), 400


@app.route("/ping", methods=['GET'])
@limiter.limit("60 per minute")
def ping():
    return jsonify({'status': "success"}), 200

