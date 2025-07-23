from flask import Blueprint, jsonify
from ..models import db, Vendor

seed_bp = Blueprint('seed', __name__)

@seed_bp.route('/seed/vendors')
def seed_vendors():
    dummy_vendors = [
        Vendor(name="ABC Steels", gst_number="GST1234", address="Chennai"),
        Vendor(name="XYZ Metals", gst_number="GST5678", address="Coimbatore"),
        Vendor(name="LMN Fabricators", gst_number="GST9012", address="Madurai")
    ]

    db.session.bulk_save_objects(dummy_vendors)
    db.session.commit()
    return jsonify({"message": "Dummy vendors added successfully!"})
