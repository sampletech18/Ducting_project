from flask import Blueprint
from app.models import db, Vendor

seed_bp = Blueprint('seed', __name__)

@seed_bp.route('/seed')
def seed():
    if Vendor.query.first():
        return "Vendors already exist."

    dummy_vendors = [
        Vendor(name='ABC Corp', gst_no='29ABCDE1234F2Z5', address='Bangalore'),
        Vendor(name='XYZ Ltd', gst_no='07XYZDE1234F1Z9', address='Delhi')
    ]
    db.session.bulk_save_objects(dummy_vendors)
    db.session.commit()
    return "Vendors seeded!"
