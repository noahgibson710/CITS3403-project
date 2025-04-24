# from flask import Flask, request, jsonify
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)  # allow frontend JS to communicate

# @app.route("/api/login", methods=["POST"])
# def api_login():
#     data = request.get_json()
#     print(data)
#     username = data.get("username")
#     password = data.get("password")

#     user = User.query.filter_by(username=username).first()
#     if user and user.password == password:
#         return jsonify({"success": True, "username": user.username})
#     else:
#         return jsonify({"success": False}), 401
