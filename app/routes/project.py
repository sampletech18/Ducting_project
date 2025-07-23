from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from ..models import db, Project, Vendor

project_bp = Blueprint('project', __name__)

# -------------------------------
# Route: Create New Project
# -------------------------------
@project_bp.route('/new_project', methods=['GET', 'POST'])
def new_project():
    vendors = Vendor.query.all()

    # Debug print to confirm vendors
    print("Loaded vendors:", [(v.id, v.name) for v in vendors])

    if request.method == 'POST':
        enquiry_id = generate_enquiry_id()
        quotation_no = request.form['quotation_no']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        location = request.form['project_location']
        vendor_id = request.form['vendor_id']
        gst = request.form['gst']
        address = request.form['address']
        incharge = request.form['incharge']
        notes = request.form['notes']
        contact = request.form.get('contact')
        email = request.form.get('email')

        diagram_file = request.files.get('source_diagram')
        filename = None
        if diagram_file:
            filename = secure_filename(diagram_file.filename)
            os.makedirs('uploads', exist_ok=True)
            diagram_file.save(os.path.join('uploads/', filename))

        project = Project(
            enquiry_id=enquiry_id,
            quotation_no=quotation_no,
            start_date=start_date,
            end_date=end_date,
            location=location,
            vendor_id=vendor_id,
            gst_number=gst,
            address=address,
            project_incharge=incharge,
            notes=notes,
            contact_number=contact,
            mail_id=email,
            source_diagram=filename
        )
        db.session.add(project)
        db.session.commit()
        flash('Project saved successfully')
        return redirect(url_for('project.new_project'))

    projects = Project.query.all()
    enquiry_id = generate_enquiry_id()
    return render_template('new_project.html', vendors=vendors, enquiry_id=enquiry_id, projects=projects)


@project_bp.route('/measurement_sheet/<int:project_id>')
def measurement_sheet(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('measurement_sheet.html', project=project)


# -------------------------------
# Route: Seed Dummy Vendors (TEMP)
# -------------------------------
@project_bp.route('/seed_vendors')
def seed_vendors():
    if not Vendor.query.first():
        v1 = Vendor(name="ABC Enterprises", gst_number="29ABCDE1234F2Z5", address="Chennai, TN")
        v2 = Vendor(name="XYZ Solutions", gst_number="33XYZDE5678G1Z9", address="Coimbatore, TN")
        db.session.add_all([v1, v2])
        db.session.commit()
        return "Dummy vendors added"
    return "Vendors already exist"

# -------------------------------
# Utility: Generate Enquiry ID
# -------------------------------
def generate_enquiry_id():
    last = Project.query.order_by(Project.id.desc()).first()
    next_num = 1 if not last else last.id + 1
    return f"VE/TN/2526/E{str(next_num).zfill(3)}"
