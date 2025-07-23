# routes/seed.py

from flask import Blueprint, jsonify
from app.models import db, Vendor  # ✅ Make sure this matches your project structure

seed_bp = Blueprint('seed', __name__)

@seed_bp.route('/seed/vendors', methods=['GET'])
def seed_vendors():
    try:
        # Optional: avoid duplicates if run multiple times
        if Vendor.query.first():
            return jsonify({"message": "Vendors already exist"}), 200

        dummy_vendors = [
            Vendor(name="Vendor A", gst_number="GSTIN001", address="Chennai"),
            Vendor(name="Vendor B", gst_number="GSTIN002", address="Coimbatore"),
            Vendor(name="Vendor C", gst_number="GSTIN003", address="Madurai"),
        ]

        db.session.bulk_save_objects(dummy_vendors)
        db.session.commit()

        return jsonify({"message": "Dummy vendors added successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
