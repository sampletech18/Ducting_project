from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
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
    enquiry_id = db.Column(db.String(50), unique=True)
    quotation = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    location = db.Column(db.String(150))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    incharge = db.Column(db.String(100))
    contact = db.Column(db.String(20))
    email = db.Column(db.String(100))
    notes = db.Column(db.Text)

    vendor = db.relationship('Vendor', backref='projects')

class MeasurementEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    duct_no = db.Column(db.String(50))
    type = db.Column(db.String(50))
    w1 = db.Column(db.Float)
    h1 = db.Column(db.Float)
    w2 = db.Column(db.Float)
    h2 = db.Column(db.Float)
    offset = db.Column(db.String(50))
    length = db.Column(db.String(50))
    qty = db.Column(db.Integer)
    factor = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ========== USERS (Dummy) ==========

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
        duct_no = request.form['duct_no']
        duct_type = request.form['duct_type']
        w1 = float(request.form['w1'])
        h1 = float(request.form['h1'])
        w2 = float(request.form['w2'])
        h2 = float(request.form['h2'])
        offset = request.form['degree_offset']
        length = request.form['length_radius']
        qty = int(request.form['quantity'])
        factor = request.form.get('factor', '1')

        new_entry = MeasurementEntry(
            duct_no=duct_no,
            type=duct_type,
            w1=w1,
            h1=h1,
            w2=w2,
            h2=h2,
            offset=offset,
            length=length,
            qty=qty,
            factor=factor
        )
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('measurement_sheet'))
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/measurement_sheet/<int:project_id>')
def measurement_sheet(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    project = Project.query.get_or_404(project_id)
    entries = MeasurementEntry.query.filter_by(project_id=project_id).all()
    return render_template('measurement_sheet.html', project=project, entries=entries)


@app.route('/submit_measurements', methods=['POST'])
def submit_measurements():
    try:
        data = request.json.get('entries', [])
        for item in data:
            entry = MeasurementEntry(
                duct_no=item.get('duct_no'),
                type=item.get('type'),
                w1=item.get('w1'),
                h1=item.get('h1'),
                w2=item.get('w2'),
                h2=item.get('h2'),
                offset=item.get('offset'),
                length=item.get('length'),
                qty=item.get('qty'),
                factor=item.get('factor')
            )
            db.session.add(entry)
        db.session.commit()
        return jsonify({'message': 'Data saved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


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
