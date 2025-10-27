from flask import Blueprint, request, jsonify, g
from app.auth.services import AuthService
from app.auth.decorators import token_required

auth_bp = Blueprint('auth', __name__)

# 注册
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    user, message = AuthService.create_user(username, email, password)

    if not user:
        return jsonify({"code": 1, "message": message}), 400

    return jsonify({
        "code": 0,
        "message": message,
        "data": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "created_at": user.created_at.isoformat()
        }
    }), 201

# 注册验证
@auth_bp.route("/verify/<token>", methods=["GET"])
def verify_email(token):
    user, message = AuthService.verify_email(token)

    if not user:
        if message == "user not found":
            return jsonify({"code": 2, "message": message}), 404
        return jsonify({"code": 1, "message": message}), 400
    
    if message == "already verified":
        return jsonify({"code": 3, "message": message}), 200

    return jsonify({"code": 0, "message": message}), 200


# 登录
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    token, message = AuthService.login_user(email, password)

    if not token:
        return jsonify({"error": message}), 401

    return jsonify({"code": 0, "message": message, "token": token})

# 获取用户信息（受保护接口）
@auth_bp.route("/profile", methods=["GET"])
@token_required
def profile():
    user = g.current_user
    return jsonify({
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    })
