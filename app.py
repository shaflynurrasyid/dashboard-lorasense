"""
app.py

This module contains the Flask application for handling user register, login,
device management, and other related functionalities.
"""

import os
import shutil
import tempfile
import csv
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask import (
    Flask, g, request, render_template, redirect, url_for,
    make_response, send_file, flash
)
from database import (
    add_device_to_db, add_user, delete_device_by_id, get_all_devices,
    get_all_users, get_user_id, get_data_by_device_and_time, get_device_data,
    get_device_info, get_device_last_data, get_user_devices, get_user_info,
    is_admin, login_user, store_data, update_device_to_db, update_user_info, user_exists
)

app = Flask(__name__)

# Load configuration from environment or default
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

# Token generation and verification
def generate_token(user_id):
    """Generate JWT token with user ID"""
    expiration = datetime.utcnow() + timedelta(minutes=30)
    return jwt.encode(
        {'user_id': user_id, 'exp': expiration}, app.config['SECRET_KEY'], algorithm='HS256'
    )

def verify_token(token):
    """Verify JWT token and decode it"""
    try:
        return jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Token is invalid

def token_required(f):
    """Decorator to check if token is required for endpoint"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token or not (decoded_token := verify_token(token)):
            return redirect(url_for('login'))
        g.current_user = decoded_token['user_id']
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token or not (decoded_token := verify_token(token)):
            return redirect(url_for('login'))
        g.current_user = decoded_token['user_id']
        user_id = g.current_user
        if not is_admin(user_id):
            return redirect(request.referrer)
        return f(*args, **kwargs)
    return decorated

# Error handler
@app.errorhandler(Exception)
def handle_exception(error):
    """Global error handler for handling exceptions"""
    app.logger.error(f"An error occurred: {error}")
    if request.referrer:
        return redirect(request.referrer)
    return redirect(url_for('home'))

# Routes
@app.route('/')
def home():
    """Render the home page"""
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user register"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        
        if password != password2:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        
        if user_exists(username) or user_exists(email):
            flash('Username or Email already exists.', 'error')
            return redirect(url_for('register'))
        
        success = add_user({
            'username': username,
            'email': email,
            'password': password
        })
        
        if success:
            flash('User registered successfully.', 'success')
            return redirect(url_for('login'))
        
        flash('Failed to register user.', 'error')
        return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        auth = request.form

        if login_user(auth):
            username = request.form.get('username')
            user_id = get_user_id(username)
            token = generate_token(user_id)
            redirect_page = 'device'
            response = make_response(redirect(url_for(redirect_page)))
            response.set_cookie('token', token, httponly=True)
            return response

        flash('Invalid username or password.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    response = make_response(redirect(url_for('login')))
    response.set_cookie('token', '', expires=0)
    return response

@app.route('/device')
@token_required
def device():
    """Render user's devices page"""
    try:
        current_user_id = g.current_user
        user_info = get_user_info(current_user_id)
        user_devices = get_user_devices(current_user_id)
        return render_template('device.html', list=user_devices, user=user_info)
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return redirect(request.referrer)

@app.route('/dashboard', methods=['GET', 'POST'])
@token_required
def dashboard():
    """Render device dashboard"""
    try:
        current_user_id = g.current_user
        user_info = get_user_info(current_user_id)
        user_devices = get_user_devices(current_user_id)
        selected_device_id = request.args.get('device_id')
        selected_time_range = request.args.get('time_range')
        
        selected_device_info = selected_device_last_data = None
        selected_device_data = []

        if selected_device_id and selected_device_id not in [
            device.device_id for device in user_devices]:
            return render_template('dashboard.html', time_range=selected_time_range,
                latest=selected_device_last_data, device_data=selected_device_data,
                device=selected_device_info, devices=user_devices, user=user_info)

        if selected_device_id:
            store_data(selected_device_id)

        selected_device_info = get_device_info(selected_device_id)
        selected_device_last_data = get_device_last_data(selected_device_id)
        selected_device_data = get_data_by_device_and_time(selected_device_id, selected_time_range)
        
        return render_template('dashboard.html', time_range=selected_time_range,
            latest=selected_device_last_data, device_data=selected_device_data,
            device=selected_device_info, devices=user_devices, user=user_info)
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return redirect(request.referrer)

@app.route('/data', methods=['GET', 'POST'])
@token_required
def data():
    """Render device data page"""
    try: 
        current_user_id = g.current_user
        user_info = get_user_info(current_user_id)
        user_devices = get_user_devices(current_user_id)

        selected_device_id = request.args.get('device_id')
        
        selected_device_info = None
        selected_device_data = []

        if selected_device_id and selected_device_id not in [
            device.device_id for device in user_devices]:
            return render_template(
                'data.html',
                data=selected_device_data,
                device=selected_device_info,
                devices=user_devices,
                user=user_info
            )        
        if selected_device_id:
            store_data(selected_device_id)

        selected_device_data = get_device_data(selected_device_id)
        selected_device_info = get_device_info(selected_device_id)

        return render_template('data.html', data=selected_device_data,
            device=selected_device_info, devices=user_devices, user=user_info)
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return redirect(request.referrer)

@app.route('/download_csv', methods=['POST'])
@token_required
def download_csv():
    """Download device data as CSV"""
    current_user_id = g.current_user

    selected_device_id = request.form.get('selected_device_id')
    user_devices = get_user_devices(current_user_id)

    # If no device is selected, redirect back with flash message
    if not selected_device_id:
        flash('Please select a device before downloading data.', 'error')
        return redirect(request.referrer)

    # Verify if the selected device belongs to the current user
    if selected_device_id not in [device.device_id for device in user_devices]:
        flash('Unauthorized.', 'error')
        return redirect(request.referrer)

    selected_device_data = get_device_data(selected_device_id)
    selected_device_info = get_device_info(selected_device_id)

    # Create CSV data
    csv_data = [["device_id", "time", "temp", "ph", "tds", "do", "orp", "salinity", "water_h", "water_cl"]]
    for row in selected_device_data:
        csv_data.append([
            row.device_id,
            str(row.time),
            str(row.temp),
            str(row.ph),
            str(row.tds),
            str(row.do),
            str(row.orp),
            str(row.salinity),
            str(row.water_h),
            str(row.water_cl)
        ])

    # Generate file name based on selected device
    csv_filename = f"{selected_device_info.device_name}_data.csv"

    # Create temporary directory
    temp_dir = tempfile.mkdtemp()

    # Create CSV file in temporary directory
    csv_filepath = os.path.join(temp_dir, csv_filename)
    with open(csv_filepath, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)

    # Create response and remove temp_dir after sending file
    try:
        response = send_file(csv_filepath, as_attachment=True)
        response.call_on_close(lambda: shutil.rmtree(temp_dir))
        return response
    except Exception as e:
        app.logger.error(f"Error occurred while sending file: {e}")
        shutil.rmtree(temp_dir)
        flash('Failed to download data.', 'error')
        return redirect(request.referrer)

@app.route('/admin-devices')
@admin_required
def admin_devices():
    """Render admin devices page"""
    try:
        current_user_id = g.current_user
        user_info = get_user_info(current_user_id)
        all_devices = get_all_devices()
        all_users = get_all_users()
        merged_data = []
        for device in all_devices:
            for user in all_users:
                if device.user_id == user.user_id:
                    merged_data.append({
                        'username': user.username,
                        'device_name': device.device_name,
                        'device_id': device.device_id,
                        'latitude': device.latitude,
                        'longitude': device.longitude
                    })
        return render_template('admin-devices.html', devices=merged_data, user=user_info)
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return redirect(request.referrer)

@app.route('/add_device', methods=['POST'])
@admin_required
def add_device():
    """Add device to the database"""
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        device_id = data.get('device_id')
        device_name = data.get('device_name')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # Validation can be added here if necessary
        if user_exists(username):
            user_id = get_user_id(username)
            success = add_device_to_db(user_id, device_id, device_name, device_name, latitude,longitude)
        else:
            flash('Username does not exist.', 'error')

        if success:
            flash('Device added successfully.', 'success')
        else:
            flash('Failed to add device.', 'error')

    return redirect(url_for('admin_devices'))

@app.route('/update_device', methods=['POST'])
@admin_required
def update_device():
    """Update device information to the database"""
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        old_device_id = data.get('old_device_id')
        device_id = data.get('device_id')
        device_name = data.get('device_name')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # Validation can be added here if necessary
        if user_exists(username):
            user_id = get_user_id(username)
            success = update_device_to_db(old_device_id, user_id, device_id, device_name, latitude,longitude)
        else:
            flash('Username does not exist.', 'error')

        if success:
            flash('Device information updated successfully.', 'success')
        else:
            flash('Failed to update device information.', 'error')

    return redirect(url_for('admin_devices'))

@app.route('/delete_device', methods=['POST'])
@admin_required
def delete_device():
    """Delete device from the database"""
    if request.method == 'POST':
        device_id = request.form.get('device_id')
        if device_id:
            success = delete_device_by_id(device_id)
            if success:
                flash('Device deleted successfully.', 'success')
            else:
                flash('Failed to delete device.', 'error')
        else:
            flash('Device ID not provided.', 'error')
    return redirect(url_for('admin_devices'))

@app.route('/admin-users')
@admin_required
def admin_users():
    """Render admin users page"""
    try:
        current_user_id = g.current_user
        user_info = get_user_info(current_user_id)
        
        all_users = get_all_users()
        return render_template('admin-users.html', users=all_users, user=user_info)
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return redirect(request.referrer)

@app.route('/profile')
@token_required
def profile():
    """Render user's profile page"""
    try:
        current_user_id = g.current_user
        user_info = get_user_info(current_user_id)
        return render_template('profile.html', user=user_info)
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return redirect(request.referrer)

@app.route('/update_user', methods=['POST'])
@token_required
def update_user():
    """Update user profile information"""
    try:
        current_user_id = g.current_user
        user_info = get_user_info(current_user_id)
        
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        new_password = request.form.get('password')
        new_password2 = request.form.get('password2')

        if new_password != new_password2:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('profile'))
        
        if new_username != user_info.username and user_exists(new_username):
            flash('Username already exists.', 'error')
            return redirect(url_for('profile'))

        success = update_user_info(current_user_id, new_username, new_email, new_password)
        
        if success:
            flash('Profile updated successfully.', 'success')
        else:
            flash('Failed to update profile.', 'error')
        
        return redirect(url_for('profile'))
    
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return redirect(request.referrer)

def main():
    """Entry point for running the Flask app"""
    app.run(debug=True)

if __name__ == '__main__':
    main()
