from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import db
from app.models import MeasurementEntry, Project
import math

measurement_bp = Blueprint('measurement', __name__, url_prefix='/measurement')

@measurement_bp.route('/sheet/<int:project_id>')
@login_required
def sheet(project_id):
    project = Project.query.get_or_404(project_id)
    entries = MeasurementEntry.query.filter_by(project_id=project_id).all()
    return render_template('measurement_sheet.html', project=project, entries=entries)

@measurement_bp.route('/add-measurement/<int:project_id>', methods=['POST'])
@login_required
def add_measurement(project_id):
    data = request.get_json()
    
    try:
        duct_no = data.get('duct_no')
        duct_type = data.get('duct_type')
        w1 = int(data.get('w1') or 0)
        h1 = int(data.get('h1') or 0)
        w2 = int(data.get('w2') or 0)
        h2 = int(data.get('h2') or 0)
        length_radius = int(data.get('length_radius') or 0)
        degree_offset = int(data.get('degree_offset') or 0)
        quantity = int(data.get('quantity') or 1)
        factor = float(data.get('factor') or 1)

        # Gauge Selection
        max_dim = max(w1, h1)
        if max_dim <= 750:
            gauge = '24g'
        elif max_dim <= 1200:
            gauge = '22g'
        elif max_dim <= 1800:
            gauge = '20g'
        else:
            gauge = '18g'

        area = 0
        if duct_type == 'st':
            area = 2 * (w1 + h1) / 1000 * (length_radius / 1000) * quantity
        elif duct_type == 'red':
            area = (w1 + h1 + w2 + h2) / 1000 * (length_radius / 1000) * quantity * factor
        elif duct_type == 'dm':
            area = (w1 * h1) / 1_000_000 * quantity
        elif duct_type == 'offset':
            area = (w1 + h1 + w2 + h2) / 1000 * ((length_radius + degree_offset) / 1000) * quantity * factor
        elif duct_type == 'shoe':
            area = ((w1 + h1) * 2) / 1000 * (length_radius / 1000) * quantity * factor
        elif duct_type == 'vanes':
            area = (w1 / 1000) * (2 * math.pi * (w1 / 1000) / 4) * quantity
        elif duct_type == 'elb':
            area = 2 * (w1 + h1) / 1000 * ((h1 / 2) / 1000 + (length_radius / 1000) * math.pi * (degree_offset / 180)) * quantity * factor

        area = round(area, 2)

        # Calculated fields
        cleat = math.ceil(area * 2)
        gasket = math.ceil(area * 2)
        bolts = math.ceil(area * 1.5)
        corner = math.ceil(quantity * 4)

        entry = MeasurementEntry(
            project_id=project_id,
            duct_no=duct_no,
            duct_type=duct_type,
            w1=w1,
            h1=h1,
            w2=w2,
            h2=h2,
            length_radius=length_radius,
            degree_offset=degree_offset,
            quantity=quantity,
            factor=factor,
            gauge=gauge,
            area=area,
            cleat=cleat,
            gasket=gasket,
            bolts=bolts,
            corner=corner,
            created_by=current_user.id
        )

        db.session.add(entry)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Entry added successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@measurement_bp.route('/get-entries/<int:project_id>', methods=['GET'])
@login_required
def get_entries(project_id):
    entries = MeasurementEntry.query.filter_by(project_id=project_id).all()
    result = []

    for e in entries:
        result.append({
            'id': e.id,
            'duct_no': e.duct_no,
            'duct_type': e.duct_type,
            'w1': e.w1,
            'h1': e.h1,
            'w2': e.w2,
            'h2': e.h2,
            'length_radius': e.length_radius,
            'degree_offset': e.degree_offset,
            'quantity': e.quantity,
            'factor': e.factor,
            'gauge': e.gauge,
            'area': e.area,
            'cleat': e.cleat,
            'gasket': e.gasket,
            'bolts': e.bolts,
            'corner': e.corner,
        })

    return jsonify(result)
