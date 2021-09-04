from flask import Flask, jsonify, request, make_response
from address import Address
from error_response import error_response

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
  return jsonify(status="api_valid")


@app.route('/test', methods=['GET'])
def ping():
  return jsonify(ping="pong")


@app.route('/validate_addresses', methods=['POST'])
def validate_addresses():
  json_data = request.get_json()

  if not json_data:
    return jsonify({})

  if type(json_data) != list:
    return error_response("data_format_invalid", 400)
  
  addresses = []

  for json_address in json_data:
    if json_address.keys() >= {"address_line_one", "city", "state"}:
      street = json_address["address_line_one"]
      city = json_address["city"]
      state = json_address["state"]  

      check_database = Address.find_address(street, city, state)

      if check_database:
        address = check_database 
      elif "zip_code" in json_address.keys():
        address = {
          "street": street,
          "city": city,
          "state": state,
          "zip_code": json_address["zip_code"],
          "candidates": 1,
          "match":"invalid"
        }
      else:
        address = {
          "street": street,
          "city": city,
          "state": state,
          "candidates": 1,
          "match":"invalid"
        }

      addresses.append(address)
    else:
      return error_response("data_format_invalid", 400)

  response = Address.call_api(addresses)
  return response
