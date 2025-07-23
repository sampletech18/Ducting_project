from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Dummy user database (replace with real DB later)
users = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'vendor1': {'password': 'vendor123', 'role': 'vendor'},
}

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

# ===== Dashboard =====
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
        # Save vendor details here...
        return "Vendor Registered Successfully!"
    return render_template('vendor_register.html')

# ===== Logout =====
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ===== Dummy Routes (You can later add real pages) =====
@app.route('/new_project')
def new_project():
    return "<h3>New Project Page (To be implemented)</h3>"

@app.route('/progress/<stage>')
def progress(stage):
    return f"<h3>Progress: {stage.replace('-', ' ').title()}</h3>"

@app.route('/summary/<type>')
def summary(type):
    return f"<h3>Summary: {type.replace('-', ' ').title()}</h3>"

@app.route('/register/employee')
def employee_register():
    return "<h3>Employee Registration Page (To be implemented)</h3>"

if __name__ == '__main__':
    app.run(debug=True)
