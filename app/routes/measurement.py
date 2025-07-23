import os
import math
from flask_login import login_required
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from app import db
from app.models import Project, Measurement
from io import BytesIO

measurement_bp = Blueprint('measurement', __name__)
UPLOAD_FOLDER = 'static/uploads'

# Save drawing images (Source Tag, Revision)
@measurement_bp.route('/upload_files/<int:project_id>', methods=['POST'])
def upload_files(project_id):
    project = Project.query.get_or_404(project_id)

    source_file = request.files.get('source_tag')
    revision_file = request.files.get('revision')

    if source_file:
        filename = secure_filename(f"{project_id}_source_{source_file.filename}")
        path = os.path.join(UPLOAD_FOLDER, filename)
        source_file.save(path)
        project.source_tag_path = path.replace('static/', '')

    if revision_file:
        filename = secure_filename(f"{project_id}_revision_{revision_file.filename}")
        path = os.path.join(UPLOAD_FOLDER, filename)
        revision_file.save(path)
        project.revision_path = path.replace('static/', '')

    db.session.commit()
    return redirect(url_for('measurement.measurement_sheet', project_id=project_id))

# Add Measurement Entry
@measurement_bp.route('/add_measurement/<int:project_id>', methods=['POST'])
def add_measurement(project_id):
    data = request.get_json()
    duct_no = data.get('duct_no')
    duct_type = data.get('duct_type')
    w1 = int(data.get('w1', 0))
    h1 = int(data.get('h1', 0))
    w2 = int(data.get('w2', 0))
    h2 = int(data.get('h2', 0))
    length = int(data.get('length', 0))
    degree = int(data.get('degree', 0))
    quantity = int(data.get('quantity', 0))
    factor = float(data.get('factor', 1))

    max_dim = max(w1, h1)
    if max_dim <= 750:
        gauge = '24g'
    elif max_dim <= 1200:
        gauge = '22g'
    elif max_dim <= 1800:
        gauge = '20g'
    else:
        gauge = '18g'

    # Area calculation
    area = 0
    if duct_type == "st":
        area = 2 * (w1 + h1) / 1000 * (length / 1000) * quantity
    elif duct_type == "red":
        area = (w1 + h1 + w2 + h2) / 1000 * (length / 1000) * quantity * factor
    elif duct_type == "dm":
        area = (w1 * h1) / 1_000_000 * quantity
    elif duct_type == "offset":
        area = (w1 + h1 + w2 + h2) / 1000 * ((length + degree) / 1000) * quantity * factor
    elif duct_type == "shoe":
        area = (w1 + h1) * 2 / 1000 * (length / 1000) * quantity * factor
    elif duct_type == "vanes":
        area = (w1 / 1000) * (2 * math.pi * (w1 / 1000) / 4) * quantity
    elif duct_type == "elb":
        area = 2 * (w1 + h1) / 1000 * ((h1 / 2) / 1000 + (length / 1000) * math.pi * (degree / 180)) * quantity * factor

    # Material calculations
    cleat = round(area * 1.2, 2)
    nuts_bolts = round(area * 0.5, 2)
    gasket = round(area * 0.3, 2)
    corner = round(area * 0.25, 2)

    # Store area only in the correct gauge column
    g24 = area if gauge == "24g" else 0
    g22 = area if gauge == "22g" else 0
    g20 = area if gauge == "20g" else 0
    g18 = area if gauge == "18g" else 0

    m = Measurement(
        project_id=project_id,
        duct_no=duct_no,
        duct_type=duct_type,
        w1=w1,
        h1=h1,
        w2=w2,
        h2=h2,
        length=length,
        degree=degree,
        quantity=quantity,
        factor=factor,
        g24=g24,
        g22=g22,
        g20=g20,
        g18=g18,
        cleat=cleat,
        nuts_bolts=nuts_bolts,
        gasket=gasket,
        corner=corner
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({'success': True})

# View measurement sheet
@measurement_bp.route('/measurement_sheet/<int:project_id>')
def measurement_sheet(project_id):
    project = Project.query.get_or_404(project_id)
    measurements = project.measurements  # Assuming relationship defined

    totals = {
        'area_24g': sum(m.g24 for m in measurements),
        'area_22g': sum(m.g22 for m in measurements),
        'area_20g': sum(m.g20 for m in measurements),
        'area_18g': sum(m.g18 for m in measurements),
        'cleat': sum(m.cleat for m in measurements),
        'bolt': sum(m.nuts_bolts for m in measurements),
        'gasket': sum(m.gasket for m in measurements),
        'corner': sum(m.corner for m in measurements),
    }

    return render_template("measurement_sheet.html", project=project, totals=totals)

# Export PDF (placeholder)
@measurement_bp.route('/export_pdf/<int:project_id>', methods=['GET'])
def export_pdf(project_id):
    return f"PDF export logic for project {project_id}"

# Export Excel (placeholder)
@measurement_bp.route('/export_excel/<int:project_id>', methods=['GET'])
def export_excel(project_id):
    return f"Excel export logic for project {project_id}"


