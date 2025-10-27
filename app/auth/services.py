from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from datetime import datetime, timedelta, timezone
import jwt

from app.extensions import db
from app.models import User
from app import mail
from loguru import logger

class AuthService:
    @staticmethod
    def generate_verify_token(email):
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return s.dumps(email, salt="email-verify")

    @staticmethod
    def confirm_verify_token(token, max_age=900):
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            email = s.loads(token, salt="email-verify", max_age=max_age)
            return email
        except Exception:
            return None

    @staticmethod
    def send_email(to, subject, body):
        msg = Message(subject=subject, recipients=[to], body=body)
        mail.send(msg)

    @staticmethod
    def create_user(username, email, password):
        if User.query.filter(User.email == email).first():
            return None, "user already exists"

        user = User(username=username, email=email)
        user.set_password(password)
        user.is_active = False
        user.is_verified = False

        db.session.add(user)
        db.session.commit()

        token = AuthService.generate_verify_token(email)
        verify_url = url_for("auth.verify_email", token=token, _external=True)
        logger.info(f"Verification link for {email}: {verify_url}")

        AuthService.send_email(to=email, subject="Verify your account", body=f"Click to verify: {verify_url}")
        
        return user, "user created, verification email sent"

    @staticmethod
    def verify_email(token):
        email = AuthService.confirm_verify_token(token)
        if not email:
            return None, "invalid or expired token"

        user = User.query.filter_by(email=email).first()
        if not user:
            return None, "user not found"

        if user.is_verified:
            return user, "already verified"

        user.is_verified = True
        user.is_active = True
        db.session.commit()
        return user, "email verified successfully"

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return None, "Invalid credentials, incorrect email or password"

        payload = {
            "id": user.id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
        return token, "login successful"

    @staticmethod
    def get_user_from_token(token):
        if not token:
            return None, "Missing token"
        if token.startswith("Bearer "):
            token = token[7:]

        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user = User.query.get(payload["id"])
            if not user:
                return None, "User not found"
            return user, "Token valid"
        except jwt.ExpiredSignatureError:
            return None, "Token expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
