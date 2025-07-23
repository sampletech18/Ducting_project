from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app.models import db, Measurement
from math import pi
from werkzeug.utils import secure_filename
import os

measurement_bp = Blueprint('measurement', __name__)
UPLOAD_FOLDER = 'uploads/'  # Make sure this directory exists

# ------------------------------------
# Upload Files for Source and Revision
# ------------------------------------
@measurement_bp.route('/upload_files/<int:project_id>', methods=['POST'])
def upload_files(project_id):
    source_file = request.files.get('source_file')
    revision_file = request.files.get('revision_file')

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if source_file:
        filename = secure_filename(f"{project_id}_source_{source_file.filename}")
        source_file.save(os.path.join(UPLOAD_FOLDER, filename))

    if revision_file:
        filename = secure_filename(f"{project_id}_revision_{revision_file.filename}")
        revision_file.save(os.path.join(UPLOAD_FOLDER, filename))

    flash("Files uploaded successfully", "success")
    return redirect(url_for('project.measurement_sheet', project_id=project_id))


# ------------------------------------
# Measurement Calculation Logic
# ------------------------------------
def calculate_measurement(data):
    w1 = int(data.get('w1', 0))
    h1 = int(data.get('h1', 0))
    w2 = int(data.get('w2', 0))
    h2 = int(data.get('h2', 0))
    length = int(data.get('length', 0))
    degree = float(data.get('degree') or 0)
    qty = int(data.get('quantity', 1))
    factor = float(data.get('factor') or 1)
    duct_type = data.get('duct_type')

    max_side = max(w1, h1)
    if max_side <= 750:
        gauge = '24g'
    elif max_side <= 1200:
        gauge = '22g'
    elif max_side <= 1800:
        gauge = '20g'
    else:
        gauge = '18g'

    area = 0
    if duct_type == 'st':
        area = 2 * (w1 + h1) / 1000 * (length / 1000) * qty
    elif duct_type == 'red':
        area = (w1 + h1 + w2 + h2) / 1000 * (length / 1000) * qty * factor
    elif duct_type == 'dm':
        area = (w1 * h1) / 1000000 * qty
    elif duct_type == 'offset':
        area = (w1 + h1 + w2 + h2) / 1000 * ((length + degree) / 1000) * qty * factor
    elif duct_type == 'shoe':
        area = (w1 + h1) * 2 / 1000 * (length / 1000) * qty * factor
    elif duct_type == 'vanes':
        area = (w1 / 1000) * (2 * pi * (w1 / 1000) / 4) * qty
    elif duct_type == 'elb':
        area = 2 * (w1 + h1) / 1000 * ((h1 / 2) / 1000 + (length / 1000) * pi * (degree / 180)) * qty * factor

    area = round(area, 3)

    g24 = area if gauge == '24g' else 0
    g22 = area if gauge == '22g' else 0
    g20 = area if gauge == '20g' else 0
    g18 = area if gauge == '18g' else 0

    cleat = int(area * 3)
    nuts_bolts = int(area * 2)
    gasket = round(area * 0.5, 2)
    corner = int(area * 2)

    return {
        'gauge': gauge,
        'area': area,
        'g24': g24,
        'g22': g22,
        'g20': g20,
        'g18': g18,
        'cleat': cleat,
        'nuts_bolts': nuts_bolts,
        'gasket': gasket,
        'corner': corner
    }


# ------------------------------------
# Create New Measurement Entry
# ------------------------------------
@measurement_bp.route('/measurement', methods=['POST'])
def create_measurement():
    data = request.json
    calc = calculate_measurement(data)

    entry = Measurement(
        duct_no=data.get('duct_no'),
        duct_type=data.get('duct_type'),
        w1=data.get('w1'),
        h1=data.get('h1'),
        w2=data.get('w2'),
        h2=data.get('h2'),
        length=data.get('length'),
        degree=data.get('degree'),
        quantity=data.get('quantity'),
        factor=data.get('factor') or 1,

        gauge=calc['gauge'],
        area=calc['area'],
        g24=calc['g24'],
        g22=calc['g22'],
        g20=calc['g20'],
        g18=calc['g18'],
        cleat=calc['cleat'],
        nuts_bolts=calc['nuts_bolts'],
        gasket=calc['gasket'],
        corner=calc['corner']
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({'message': 'Measurement added successfully'}), 201


# ------------------------------------
# Get All Entries
# ------------------------------------
@measurement_bp.route('/measurement', methods=['GET'])
def get_all_measurements():
    measurements = Measurement.query.all()
    result = []
    for m in measurements:
        result.append({
            'id': m.id,
            'duct_no': m.duct_no,
            'duct_type': m.duct_type,
            'w1': m.w1,
            'h1': m.h1,
            'w2': m.w2,
            'h2': m.h2,
            'length': m.length,
            'degree': m.degree,
            'quantity': m.quantity,
            'factor': m.factor,
            'gauge': m.gauge,
            'area': m.area,
            'g24': m.g24,
            'g22': m.g22,
            'g20': m.g20,
            'g18': m.g18,
            'cleat': m.cleat,
            'nuts_bolts': m.nuts_bolts,
            'gasket': m.gasket,
            'corner': m.corner
        })
    return jsonify(result)


# ------------------------------------
# Delete Entry
# ------------------------------------
@measurement_bp.route('/measurement/<int:id>', methods=['DELETE'])
def delete_measurement(id):
    entry = Measurement.query.get(id)
    if entry:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Deleted successfully'})
    return jsonify({'message': 'Entry not found'}), 404
