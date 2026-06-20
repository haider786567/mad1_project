# models.py

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    role = db.Column(
        db.String(20),
        nullable=False,
        default="user"
    )
    
    role = db.Column(
        db.String(20),
        nullable=False,
        default="user"
    )
    
    status = db.Column(
        db.String(20),
        nullable=False,
        default="approved"
    )

    is_admin = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class StaffProfile(db.Model):

    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    contact_number = db.Column(db.String(20))

    status = db.Column(
        db.String(20),
        default="active"
    )

    user = db.relationship(
        "User",
        backref="staff_profile"
    )


class Trek(db.Model):

    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)

    trek_name = db.Column(
        db.String(150),
        nullable=False
    )

    location = db.Column(
        db.String(150),
        nullable=False
    )

    difficulty = db.Column(
        db.String(20),
        nullable=False
    )

    duration = db.Column(
        db.Integer,
        nullable=False
    )

    available_slots = db.Column(
        db.Integer,
        nullable=False
    )

    assigned_staff_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    status = db.Column(
        db.String(20),
        default="pending"
    )

    start_date = db.Column(
        db.Date,
        nullable=False
    )

    end_date = db.Column(
        db.Date,
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    assigned_staff = db.relationship(
        "User",
        backref="assigned_treks"
    )


class Booking(db.Model):
    

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("treks.id"),
        nullable=False
    )

    booking_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    status = db.Column(
        db.String(20),
        default="booked"
    )

    user = db.relationship(
        "User",
        backref="bookings"
    )

    trek = db.relationship(
        "Trek",
        backref="bookings"
    )
    
