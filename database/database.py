import asyncpg as sql
from utils.utils import calculate_distance
import json


class DataBase:
    def __init__(self, host: str, database: str, password: str, user: str = 'postgres', port: str = '5432'):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    async def fetchrow(self, query, *args):
        con = await sql.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password)
        data = await con.fetchrow(query, *args)
        await con.close()
        return data

    async def fetch(self, query, *args):
        con = await sql.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password)
        data = await con.fetch(query, *args)
        await con.close()
        return data

    async def execute(self, query, *args):
        con = await sql.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password)
        await con.execute(query, *args)
        await con.close()

    async def create_db(self):
        await DataBase.execute(self, "CREATE TABLE IF NOT EXISTS tokens("
                                     "token VARCHAR default Null)")

    async def check_token(self, token):
        token = await DataBase.fetchrow(self, "SELECT * FROM tokens WHERE token = $1", token)
        if not token:
            return False
        else:
            return token

    async def get_cities_by_coordinates(self, lat: float, lng: float, radius: int = 30, limit: int = 20) \
            -> json:
        """
        :param lat: Latitude
        :param lng: Longitude
        :param radius: Radius of the search
        :param limit: Limit of cities to return
        :return dict or bool:
        """

        response = {}
        cities = await DataBase.fetch(self,
                                      f'SELECT * FROM cities '
                                      f'WHERE lat BETWEEN {lat} - {radius / 111} '
                                      f'AND {lat} + {radius / 111}'
                                      f'AND lng BETWEEN {lng} - {radius / 111} '
                                      f'AND {lng} + {radius / 111} '
                                      f'LIMIT {limit}')
        if not cities:
            return False

        for city in cities:
            response[city["name"]] = {'name': city['name'],
                                      'ascii': city['ASCII Name'],
                                      'other_names': city['Alternate Names'],
                                      'lat': city['lat'],
                                      'lng': city['lng'],
                                      'country_en': city['Country name EN'],
                                      'contry_code': city['Country Code'],
                                      'population': city['population'],
                                      'distance': calculate_distance(lat,
                                                                     lng,
                                                                     city['lat'],
                                                                     city['lng'])}

        return json.dumps(response, indent=4)

    async def get_cities_by_name(self, city: str, radius: int = 30, limit: int = 20) -> json:
        """
        :param city: Any possible and RIGHT name of the city you're looking for
        :param radius: Radius of the search
        :param limit: Limit of cities to return
        :return dict:
        """
        con = await sql.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password)

        response = {}
        city_parent = await DataBase.fetchrow(self,
                                              'SELECT * FROM cities '
                                              'WHERE LOWER($1) = ANY (SELECT LOWER(unnest("Alternate Names"))) '
                                              'ORDER BY population DESC LIMIT 1',
                                              city)
        if not city_parent:
            city_parent = await DataBase.fetchrow(self,
                                                  'SELECT * FROM cities '
                                                  'WHERE LOWER($1) = LOWER(name) '
                                                  'ORDER BY population DESC LIMIT 1',
                                                  city)
            if not city_parent:
                city_parent = await DataBase.fetchrow(self,
                                                      'SELECT * FROM cities '
                                                      'WHERE LOWER($1) = LOWER("ASCII Name") '
                                                      'ORDER BY population DESC LIMIT 1',
                                                      city)
                if not city_parent:
                    return False

        cities = await DataBase.fetch(self,
                                      f'SELECT * FROM cities '
                                      f'WHERE lat BETWEEN {city_parent["lat"]} - {radius / 111} '
                                      f'AND {city_parent["lat"]} + {radius / 111}'
                                      f'AND lng BETWEEN {city_parent["lng"]} - {radius / 111} '
                                      f'AND {city_parent["lng"]} + {radius / 111} '
                                      f'LIMIT {limit}')

        for city in cities:
            response[city["name"]] = {'name': city['name'],
                                      'ascii': city['ASCII Name'],
                                      'other_names': city['Alternate Names'],
                                      'lat': city['lat'],
                                      'lng': city['lng'],
                                      'country_en': city['Country name EN'],
                                      'contry_code': city['Country Code'],
                                      'population': city['population'],
                                      'distance': calculate_distance(city_parent['lat'],
                                                                     city_parent['lng'],
                                                                     city['lat'],
                                                                     city['lng'])}

        return json.dumps(response, indent=4)