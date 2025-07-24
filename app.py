from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import math
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# PostgreSQL Render DB URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://duct_db_user:SXQ9iAKpluAXibt4xcxhakJk4uoQCFko@dpg-d2075pp5pdvs73c6q740-a.singapore-postgres.render.com/duct_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ========== MODELS ==========

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    gst = db.Column(db.String(50))
    address = db.Column(db.String(250))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.String(100))
    quotation = db.Column(db.String(200))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    location = db.Column(db.String(100))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    vendor = db.relationship('Vendor', backref='projects')
    incharge = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    email = db.Column(db.String(100))
    notes = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    duct_no = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    
    w1 = db.Column(db.Float, default=0)
    h1 = db.Column(db.Float, default=0)
    w2 = db.Column(db.Float, default=0)
    h2 = db.Column(db.Float, default=0)
    degree = db.Column(db.Float, default=0)
    length = db.Column(db.Float, default=0)
    
    qty = db.Column(db.Integer, default=1)
    factor = db.Column(db.Float, default=1.0)

    area = db.Column(db.Float, default=0.0)

    g24 = db.Column(db.Float, default=0.0)
    g22 = db.Column(db.Float, default=0.0)
    g20 = db.Column(db.Float, default=0.0)
    g18 = db.Column(db.Float, default=0.0)

    bolts = db.Column(db.Integer, default=0)
    cleat = db.Column(db.Integer, default=0)
    gasket = db.Column(db.Integer, default=0)
    corner = db.Column(db.Integer, default=0)

    project = db.relationship('Project', backref=db.backref('measurements', lazy=True))
# ========== USERS ==========

users = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'vendor1': {'password': 'vendor123', 'role': 'vendor'},
}

# ========== ROUTES ==========

@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            msg = 'Invalid credentials'
    return render_template('login.html', msg=msg)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['username'], role=session['role'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/new_project', methods=['GET', 'POST'])
def new_project():
    if 'username' not in session:
        return redirect(url_for('login'))

    enquiry_id = f"VE/TN/2526/E{random.randint(100, 999)}"

    if request.method == 'POST':
        vendor_name = request.form['vendor']
        vendor = Vendor.query.filter_by(name=vendor_name).first()

        new_project = Project(
            enquiry_id=request.form['enquiry_id'],
            quotation=request.form['quotation'],
            start_date=request.form['start_date'],
            end_date=request.form['end_date'],
            location=request.form['location'],
            vendor=vendor,
            incharge=request.form['incharge'],
            contact=request.form['contact'],
            email=request.form['mail'],
            notes=request.form['notes']
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('new_project'))

    vendors = Vendor.query.all()
    projects = Project.query.all()
    return render_template('new_project.html', enquiry_id=enquiry_id, vendors=vendors, projects=projects)

@app.route('/register/vendor', methods=['GET', 'POST'])
def vendor_register():
    if request.method == 'POST':
        vendor = Vendor(
            name=request.form['vendor_name'],
            gst=request.form['gst_number'],
            address=request.form['address']
        )
        db.session.add(vendor)
        db.session.commit()
        return "Vendor Registered Successfully!"
    return render_template('vendor_register.html')

@app.route('/add_measurement', methods=['POST'])
def add_measurement():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        project_id = int(request.form['project_id'])
        duct_no = request.form['duct_no']
        duct_type = request.form['duct_type']
        w1 = float(request.form.get('w1') or 0)
        h1 = float(request.form.get('h1') or 0)
        w2 = float(request.form.get('w2') or 0)
        h2 = float(request.form.get('h2') or 0)
        length = float(request.form.get('length_radius') or 0)
        degree = float(request.form.get('degree_offset') or 0)
        qty = int(request.form.get('quantity') or 1)
        factor = float(request.form.get('factor') or 1)

        # AREA CALCULATION
        area = 0
        if duct_type == "ST":
            area = 2 * (w1 + h1) / 1000 * (length / 1000) * qty
        elif duct_type == "RED":
            area = (w1 + h1 + w2 + h2) / 1000 * (length / 1000) * qty * factor
        elif duct_type == "DM":
            area = (w1 * h1) / 1000000 * qty
        elif duct_type == "OFFSET":
            area = (w1 + h1 + w2 + h2) / 1000 * ((length + degree) / 1000) * qty * factor
        elif duct_type == "SHOE":
            area = (w1 + h1) * 2 / 1000 * (length / 1000) * qty * factor
        elif duct_type == "VANES":
            area = (w1 / 1000) * (2 * math.pi * (w1 / 1000) / 4) * qty
        elif duct_type == "ELB":
            arc = (length / 1000) * math.pi * (degree / 180)
            area = 2 * (w1 + h1) / 1000 * (((h1 / 2) / 1000) + arc) * qty * factor

        # HARDWARE CALCULATION
        perimeter = w1 + h1 + w2 + h2
        nuts_bolts = (perimeter / 1000) * 8 * qty
        cleat = (perimeter / 1000) * 4 * qty
        gasket = (perimeter / 1000) * qty
        corner_pieces = 4 * qty

        new_entry = MeasurementEntry(
            project_id=project_id,
            duct_no=duct_no,
            type=duct_type,
            w1=w1,
            h1=h1,
            w2=w2,
            h2=h2,
            offset=degree,
            length=length,
            qty=qty,
            factor=factor,
            area=round(area, 3),
            nuts_bolts=round(nuts_bolts, 2),
            cleat=round(cleat, 2),
            gasket=round(gasket, 2),
            corner_pieces=corner_pieces
        )

        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('measurement_sheet', project_id=project_id))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"



@app.route('/measurement_sheet/<int:project_id>', methods=['GET', 'POST'])
def measurement_sheet(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        duct_no = request.form['duct_no']
        type = request.form['type']
        w1 = float(request.form.get('w1') or 0)
        h1 = float(request.form.get('h1') or 0)
        w2 = float(request.form.get('w2') or 0)
        h2 = float(request.form.get('h2') or 0)
        degree = float(request.form.get('degree') or 0)
        length = float(request.form.get('length') or 0)
        qty = int(request.form.get('qty') or 1)
        factor = float(request.form.get('factor') or 1)

        area = 0
        if type == 'ST':
            area = 2 * ((w1 + h1) * length) / 1000000
        elif type == 'ELB':
            area = 2 * ((w1 + h1) * (1.57 * (w1 + h1) / 2)) / 1000000
        elif type == 'RED':
            area = ((w1 + h1 + w2 + h2) * length) / 1000000
        elif type == 'DM':
            area = 2 * ((w1 + h1 + w2 + h2) * length) / 2000000
        elif type == 'OFFSET':
            area = 2 * ((w1 + h1) * length) / 1000000
        elif type == 'SHOE':
            area = 2 * ((w1 + h1) * length) / 1000000
        elif type == 'VANES':
            area = ((w1 * h1) * 1.2) / 1000000

        area = area * qty * factor
        g24 = g22 = g20 = g18 = 0

        if max(w1, w2) <= 750 and max(h1, h2) <= 750:
            g24 = area
        elif 751 <= max(w1, w2) <= 1200 or 751 <= max(h1, h2) <= 1200:
            g22 = area
        elif 1201 <= max(w1, w2) <= 1800 or 1201 <= max(h1, h2) <= 1800:
            g20 = area
        else:
            g18 = area

        bolts = round((area * 12) / 100)
        cleat = round((area * 15) / 100)
        gasket = round((area * 10) / 100)
        corner = round((area * 8) / 100)

        new_entry = Measurement(
            duct_no=duct_no,
            type=type,
            w1=w1,
            h1=h1,
            w2=w2,
            h2=h2,
            degree=degree,
            length=length,
            qty=qty,
            factor=factor,
            area=round(area, 2),
            g24=round(g24, 2),
            g22=round(g22, 2),
            g20=round(g20, 2),
            g18=round(g18, 2),
            bolts=bolts,
            cleat=cleat,
            gasket=gasket,
            corner=corner,
            project_id=project_id
        )
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('measurement_sheet', project_id=project_id))

    measurements = Measurement.query.filter_by(project_id=project_id).all()
    total_qty = sum(m.qty for m in measurements)
    total_area = round(sum(m.area for m in measurements), 2)
    total_24g = round(sum(m.g24 for m in measurements), 2)
    total_22g = round(sum(m.g22 for m in measurements), 2)
    total_20g = round(sum(m.g20 for m in measurements), 2)
    total_18g = round(sum(m.g18 for m in measurements), 2)
    total_bolts = sum(m.bolts for m in measurements)
    total_cleat = sum(m.cleat for m in measurements)
    total_gasket = sum(m.gasket for m in measurements)
    total_corner = sum(m.corner for m in measurements)

    return render_template('measurement_sheet.html',
        project=project,
        measurements=measurements,
        total_qty=total_qty,
        total_area=total_area,
        total_24g=total_24g,
        total_22g=total_22g,
        total_20g=total_20g,
        total_18g=total_18g,
        total_bolts=total_bolts,
        total_cleat=total_cleat,
        total_gasket=total_gasket,
        total_corner=total_corner,
        project_id=project_id
                          )

@app.route('/init_db')
def init_db():
    try:
        db.drop_all()
        db.create_all()

        sample_vendors = [
            Vendor(name="Perfect Fabricators", gst="29ABCDE1234F1Z5", address="Chennai, TN"),
            Vendor(name="Duct Tech Engineers", gst="29FGHIJ5678K9Z5", address="Coimbatore, TN"),
            Vendor(name="Sheet Metal Works", gst="29KLMNO9876P1Z5", address="Madurai, TN")
        ]
        db.session.add_all(sample_vendors)
        db.session.commit()

        return "✅ Database reset & vendors added successfully!"
    except Exception as e:
        return f"❌ Failed: {str(e)}"

# ========== Run ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
