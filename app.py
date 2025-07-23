from flask import Flask, render_template, request, redirect, url_for, session
import random
import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# ===== Dummy user database =====
users = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'vendor1': {'password': 'vendor123', 'role': 'vendor'},
}

# ===== Dummy vendors =====
dummy_vendors = [
    {
        'name': 'Veer Industries',
        'gst': '33AABCV1234D1Z2',
        'address': '12, SIDCO Industrial Estate, Chennai'
    },
    {
        'name': 'Max Fabricators',
        'gst': '29AACCM9988Q1Z5',
        'address': 'Plot 22, Jigani Layout, Bangalore'
    },
    {
        'name': 'SteelTech Pvt Ltd',
        'gst': '27AAACI1234P1Z6',
        'address': 'MIDC Area, Pune'
    }
]

# ===== Dummy project list =====
projects = []

# ===== Login Page =====
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

# ===== Dashboard Page =====
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['username'], role=session['role'])

# ===== Vendor Registration =====
@app.route('/register/vendor', methods=['GET', 'POST'])
def vendor_register():
    if request.method == 'POST':
        vendor_name = request.form['vendor_name']
        gst_number = request.form['gst_number']
        address = request.form['address']
        # Save logic here
        return "Vendor Registered Successfully!"
    return render_template('vendor_register.html')

# ===== New Project Form =====
@app.route('/new_project', methods=['GET', 'POST'])
def new_project():
    if 'username' not in session:
        return redirect(url_for('login'))

    enquiry_id = f"VE/TN/2526/E{str(random.randint(100,999))}"

    if request.method == 'POST':
        data = {
            'enquiry_id': request.form['enquiry_id'],
            'quotation': request.form['quotation'],
            'start_date': request.form['start_date'],
            'end_date': request.form['end_date'],
            'location': request.form['location'],
            'vendor': request.form['vendor'],
            'gst': request.form['gst'],
            'address': request.form['address'],
            'incharge': request.form['incharge'],
            'contact': request.form['contact'],
            'email': request.form['email'],
            'notes': request.form['notes']
        }
        projects.append(data)
        return redirect(url_for('new_project'))

    return render_template('new_project.html', enquiry_id=enquiry_id, vendors=dummy_vendors, projects=projects)

# ===== Logout =====
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
