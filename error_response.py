from flask import jsonify, make_response

def error_response(error, status_code):
  response = make_response(
              jsonify({
                "error": error
              }),
              status_code,
            )
  response.headers["Content-Type"] = "application/json"
  return response