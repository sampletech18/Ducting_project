from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# --------------------------
# User Model
# --------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)

# --------------------------
# Vendor Model
# --------------------------
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    gst_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)

# --------------------------
# Project Model
# --------------------------
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.String(50), unique=True, nullable=False)
    quotation_no = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    source_diagram = db.Column(db.String(200), nullable=True)

    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    vendor = db.relationship('Vendor', backref='projects')

    gst_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    project_incharge = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    mail_id = db.Column(db.String(100), nullable=True)

# --------------------------
# Measurement Model
# --------------------------
class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    duct_no = db.Column(db.String(50), nullable=False)
    duct_type = db.Column(db.String(20), nullable=False)
    w1 = db.Column(db.Integer, nullable=False)
    h1 = db.Column(db.Integer, nullable=False)
    w2 = db.Column(db.Integer, nullable=False)
    h2 = db.Column(db.Integer, nullable=False)
    length = db.Column(db.Integer, nullable=False)
    degree = db.Column(db.String(20), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    factor = db.Column(db.Float, nullable=True)

    gauge = db.Column(db.String(10), nullable=False)
    area = db.Column(db.Float, nullable=False)
    g24 = db.Column(db.Float, default=0)
    g22 = db.Column(db.Float, default=0)
    g20 = db.Column(db.Float, default=0)
    g18 = db.Column(db.Float, default=0)

    nuts_bolts = db.Column(db.Integer, default=0)
    cleat = db.Column(db.Integer, default=0)
    gasket = db.Column(db.Float, default=0.0)
    corner = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
