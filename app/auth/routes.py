from flask import Blueprint, redirect, request, jsonify, g
from app.auth.services import AuthService
from app.auth.decorators import token_required
import os
import requests
from urllib.parse import urlencode

auth_bp = Blueprint("auth", __name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


# Step 1: 跳转到 Google 登录
@auth_bp.route("/google/login")
def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    )
    return redirect(google_auth_url)


# Step 2: Google 回调
@auth_bp.route("/google/callback")
def google_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"code": 1, "message": "Missing code"}), 400

    # 用 code 换取 access token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    token_resp = requests.post(token_url, data=token_data).json()
    access_token = token_resp.get("access_token")

    if not access_token:
        return (
            jsonify(
                {"code": 1, "message": "Failed to get access token", "data": token_resp}
            ),
            400,
        )

    # 获取用户信息
    user_info_resp = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    ).json()

    email = user_info_resp.get("email")
    name = user_info_resp.get("name")

    user, token = AuthService.login_or_register_google_user(email, name)

    return jsonify(
        {
            "code": 0,
            "message": "Google login successful",
            "data": {"email": email, "name": name, "token": token},
        }
    )


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

    return (
        jsonify(
            {
                "code": 0,
                "message": message,
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "created_at": user.created_at.isoformat(),
                },
            }
        ),
        201,
    )


# 注册验证
@auth_bp.route("/verify/<token>", methods=["GET"])
def verify_email(token):
    user, message = AuthService.verify_email(token)

    if not user:
        code = 2 if message == "user not found" else 1
        return jsonify({"code": code, "message": message}), 404 if code == 2 else 400

    code = 3 if message == "already verified" else 0
    return jsonify({"code": code, "message": message}), 200


# 登录
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    token, message = AuthService.login_user(email, password)

    if not token:
        return jsonify({"code": 1, "message": message}), 401

    return jsonify({"code": 0, "message": message, "data": {"token": token}})


# 获取用户信息（受保护接口）
@auth_bp.route("/profile", methods=["GET"])
@token_required
def profile():
    user = g.current_user
    return jsonify(
        {
            "code": 0,
            "message": "User profile fetched successfully",
            "data": {
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
            },
        }
    )
