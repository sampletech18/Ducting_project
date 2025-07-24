from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ducting.db'
db = SQLAlchemy(app)

# Models
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gst_number = db.Column(db.String(15))
    address = db.Column(db.String(200))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    vendor = db.relationship('Vendor', backref=db.backref('projects', lazy=True))

class MeasurementEntry(db.Model):
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
    nuts_bolts = db.Column(db.Float, default=0.0)
    cleat = db.Column(db.Float, default=0.0)
    gasket = db.Column(db.Float, default=0.0)
    corner_pieces = db.Column(db.Integer, default=0)

# Helpers
def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0

def safe_int(val):
    try:
        return int(val)
    except:
        return 0

def apply_duct_calculation(entry):
    w1, h1, w2, h2 = entry.w1, entry.h1, entry.w2, entry.h2
    qty, factor = entry.qty, entry.factor
    if entry.type == 'ST':
        area = 2 * (w1 + h1) * factor * qty / 92900
    elif entry.type == 'RED':
        area = 2 * ((w1 + w2) / 2 + (h1 + h2) / 2) * factor * qty / 92900
    elif entry.type == 'DM':
        area = 2 * (w1 + h1) * factor * qty / 92900
    elif entry.type == 'OFFSET':
        area = 2 * (w1 + h1) * factor * qty / 92900
    elif entry.type == 'SHOE':
        area = 2 * ((w1 + w2) / 2 + (h1 + h2) / 2) * factor * qty / 92900
    elif entry.type == 'VANES':
        area = 0.1 * factor * qty
    elif entry.type == 'ELB':
        area = 2 * (w1 + h1) * factor * qty / 92900
    else:
        area = 0

    entry.area = round(area, 2)
    entry.nuts_bolts = round(area * 1.1, 2)
    entry.cleat = round(area * 0.5, 2)
    entry.gasket = round(area * 0.6, 2)
    entry.corner_pieces = qty * 4

# Routes
@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    projects = Project.query.all()
    return render_template('dashboard.html', projects=projects)

@app.route('/add_project', methods=['POST'])
def add_project():
    name = request.form['name']
    location = request.form['location']
    vendor_id = request.form['vendor_id']
    new_project = Project(name=name, location=location, vendor_id=vendor_id)
    db.session.add(new_project)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/vendors')
def vendors():
    vendor_list = Vendor.query.all()
    return render_template('vendors.html', vendors=vendor_list)

@app.route('/vendor_register', methods=['GET', 'POST'])
def vendor_register():
    if request.method == 'POST':
        name = request.form['name']
        gst_number = request.form['gst_number']
        address = request.form['address']
        new_vendor = Vendor(name=name, gst_number=gst_number, address=address)
        db.session.add(new_vendor)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('vendor_register.html')

@app.route('/measurement_sheet/<int:project_id>', methods=['GET', 'POST'])
def measurement_sheet(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        entry = MeasurementEntry(
            project_id=project_id,
            duct_no=request.form['duct_no'],
            type=request.form['type'],
            w1=safe_float(request.form.get('w1')),
            h1=safe_float(request.form.get('h1')),
            w2=safe_float(request.form.get('w2')),
            h2=safe_float(request.form.get('h2')),
            degree=safe_float(request.form.get('degree')),
            length=safe_float(request.form.get('length')),
            qty=safe_int(request.form.get('qty')),
            factor=safe_float(request.form.get('factor'))
        )
        apply_duct_calculation(entry)
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('measurement_sheet', project_id=project_id))

    measurements = MeasurementEntry.query.filter_by(project_id=project_id).all()
    total_area = sum(m.area for m in measurements)
    total_qty = sum(m.qty for m in measurements)
    return render_template('measurement_sheet.html', project=project, measurements=measurements, total_area=total_area, total_qty=total_qty)

@app.route('/export_measurements/<int:project_id>')
def export_measurements(project_id):
    measurements = MeasurementEntry.query.filter_by(project_id=project_id).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Duct No', 'Type', 'W1', 'H1', 'W2', 'H2', 'Degree', 'Length', 'Qty', 'Factor', 'Area', 'Nuts & Bolts', 'Cleat', 'Gasket', 'Corner Pieces'])
    for m in measurements:
        writer.writerow([m.duct_no, m.type, m.w1, m.h1, m.w2, m.h2, m.degree, m.length, m.qty, m.factor, m.area, m.nuts_bolts, m.cleat, m.gasket, m.corner_pieces])
    output.seek(0)
    return output.getvalue()

@app.route('/init_db')
def init_db():
    db.create_all()
    return "Database tables created successfully!"

if __name__ == '__main__':
    app.run(debug=True)
