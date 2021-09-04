import os
import uuid
import requests
import json

from flask import jsonify
from error_response import error_response

global_address_objects = []

class Address:
    id = uuid.uuid4()
    address_line_one = None
    city = None
    state = None
    zip_code = None
    latitude = None
    longitude = None

    def __init__(self, address_line_one=None, city=None, state=None, zip_code=None, latitude = None, longitude = None):
        self.address_line_one = address_line_one
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.latitude = latitude
        self.longitude = longitude

    # returns a dictionary version of the address object
    def to_dict(self):
        return {
            "address_line_one": self.address_line_one,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "latitude": self.latitude,
            "longitude": self.longitude
        }

    # calls SmartyStreets API and returns a properly formatted response with 
    # correct status code and new information from API
    def call_api(addresses):
        auth_id = os.environ.get('AUTH_ID')
        auth_token = os.environ.get('AUTH_TOKEN')

        url = 'https://us-street.api.smartystreets.com/street-address?auth-id={}&auth-token={}'.format(auth_id, auth_token)

        final_addresses = []
        for address in addresses:
            if type(address) == Address:
                final_addresses.append(address)
            else:
                response = requests.post(url, data = json.dumps([address]))
                address_object = Address.parse_json_response(response.json()[0], response.status_code)
                if isinstance(address_object, Address):
                    final_addresses.append(address_object)
                else:
                    return address_object
        return Address.format_addresses_to_response(final_addresses)
    
    # returns an error response if data is misformed from the SmartyStreets API or returns an address object if
    # everything is sucessful
    def parse_json_response(json, status_code):
        if status_code != 200:
            return error_response(json, status_code)

        try:
            metadata = json["metadata"]
                
            if metadata["precision"] == "Unknown":
                return error_response("address_not_found", 422)
            
            components = json["components"]
            address_object = Address(json["delivery_line_1"],
                                        components["city_name"], 
                                        components["state_abbreviation"],
                                        components["zipcode"],
                                        metadata["latitude"],
                                        metadata["longitude"]
                                    )

            Address.add_address(address_object)
            
            return address_object
        except KeyError:
            return error_response("bad_gateway", 502)

    # returns address object based on either a combination of street, city, state or latitude and longitude
    def find_address(street = None, city = None, state = None, latitude = None, longitude = None):
        for address in global_address_objects:
            if latitude and longitude and address.latitude == latitude and address.longitude == longitude:
                return address
            elif street and city and state and address.address_line_one == street and address.city == city and address.state == state:
                return address
        return None

    # adds the address to the database only if there is no existing address with same coordinates
    def add_address(address):
        check_database = Address.find_address(latitude=address.latitude, longitude=address.longitude)
        if not check_database:
            global_address_objects.append(address)
    
    # formats final addresses to a json response with status 200
    def format_addresses_to_response(addresses):
        json_array = []
        for address in addresses:
            json_array.append(address.to_dict())
        
        return jsonify(json_array)
