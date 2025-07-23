from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required
from app import db
from models import Project, Measurement

measurement_bp = Blueprint('measurement', __name__, url_prefix='/measurement')


@measurement_bp.route('/sheet/<int:project_id>')
@login_required
def measurement_sheet(project_id):
    project = Project.query.get_or_404(project_id)
    entries = Measurement.query.filter_by(project_id=project_id).all()
    return render_template('measurement_sheet.html', project=project, entries=entries)


@measurement_bp.route('/add-measurement/<int:project_id>', methods=['POST'])
@login_required
def add_measurement(project_id):
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data received'})

    try:
        w1 = float(data.get('w1') or 0)
        h1 = float(data.get('h1') or 0)
        area = round((w1 * h1) / 1000000, 2)
        gauge = ''
        if w1 <= 751 and h1 <= 751:
            gauge = '24g'
        elif w1 <= 1201 and h1 <= 1201:
            gauge = '22g'
        elif w1 <= 1800 and h1 <= 1800:
            gauge = '20g'
        else:
            gauge = '18g'

        entry = Measurement(
            project_id=project_id,
            duct_no=data.get('duct_no'),
            duct_type=data.get('duct_type'),
            w1=w1,
            h1=h1,
            w2=float(data.get('w2') or 0),
            h2=float(data.get('h2') or 0),
            length=float(data.get('length') or 0),
            degree_offset=float(data.get('degree_offset') or 0),
            quantity=int(data.get('quantity') or 1),
            factor=float(data.get('factor') or 1),
            gauge=gauge,
            area=area,
            cleat=area * 0.1,
            bolts=area * 0.05,
            gasket=area * 0.08,
            corner=area * 0.02
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@measurement_bp.route('/submit/<int:project_id>')
@login_required
def submit_measurement(project_id):
    # Handle submission logic here
    return redirect(url_for('measurement.measurement_sheet', project_id=project_id))


@measurement_bp.route('/export/pdf/<int:project_id>')
@login_required
def export_pdf(project_id):
    return f"PDF Export for Project {project_id}"


@measurement_bp.route('/export/excel/<int:project_id>')
@login_required
def export_excel(project_id):
    return f"Excel Export for Project {project_id}"
