"""
database.py

This module contains SQLAlchemy ORM definitions and database operations for a 
system managing users, devices, and data entries. It includes classes for User, 
Device, and Data, along with functions to interact with these entities such as 
adding users, retrieving device data, and storing data fetched from an external API.
"""

import os
import json
from datetime import datetime, timedelta
import bcrypt
from sqlalchemy import (
    create_engine, desc, Column, Float, DateTime,
    Boolean, String, ForeignKey, Integer, or_
)
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, relationship
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from fetch_data import fetch_data_api_antares

# Load environment variables from the .env file
load_dotenv()

# Retrieve the variables from the environment
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
hostname = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')
app_lora = os.getenv('APP_LORA')
api_key = os.getenv('API_KEY_ANTARES')

# Construct the connection URL
connection_url = f'mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}'

# Create the SQLAlchemy engine
engine = create_engine(connection_url)

# Define the base class for declarative class definitions
Base = declarative_base()

class User(Base):
    """
    Represents a user in the database.

    Attributes:
        __tablename__ (str): The name of the database table.
        user_id (int): Primary key representing the user identifier.
        username (str): Username of the user.
        email (str): Email address of the user.
        password (str): Hashed password of the user.
        admin (bool): Indicates if the user has admin privileges.

    Relationships:
        devices (relationship): One-to-many relationship with Device objects.
    """
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100))
    email = Column(String(100))
    password = Column(String(100))
    admin = Column(Boolean, default=False)

    devices = relationship('Device', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hashes and sets the user's password"""
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Checks if the provided password matches the user's hashed password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class Device(Base):
    """
    Represents a device in the database.

    Attributes:
        __tablename__ (str): The name of the database table.
        device_id (str): Primary key representing the device identifier.
        device_name (str): Name of the device.
        user_id (int): Foreign key referencing the user identifier associated with the device.

    Relationships:
        user (relationship): Many-to-one relationship with User objects.
        data (relationship): One-to-many relationship with Data objects.
    """
    __tablename__ = 'device'
    device_id = Column(String(100), primary_key=True)
    device_name = Column(String(100))
    latitude = Column(String(100))
    longitude = Column(String(100))
    user_id = Column(Integer, ForeignKey('user.user_id'))

    user = relationship('User', back_populates='devices')
    data = relationship('Data', back_populates='device', cascade='all, delete-orphan')

class Data(Base):
    """
    Represents data entries from devices in the database.

    Attributes:
        __tablename__ (str): The name of the database table.
        data_id (int): Primary key representing the data entry identifier.
        device_id (str): Foreign key referencing the device identifier.
        time (DateTime): Timestamp of the data entry.
        temp (float): Temperature reading.
        ph (float): pH reading.
        tds (float): Total Dissolved Solids reading.
        do (float): Dissolved Oxygen reading.
        orp (float): Oxidation-Reduction Potential reading.
        salinity (float): Salinity reading.
        water_h (float): Water hardness reading.
        water_cl (float): Water chlorine reading.

    Relationships:
        device (relationship): Many-to-one relationship with Device objects.
    """
    __tablename__ = 'data'
    data_id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(100), ForeignKey('device.device_id'))
    time = Column(DateTime)
    temp = Column(Float)
    ph = Column(Float)
    tds = Column(Float)
    do = Column(Float)
    orp = Column(Float)
    salinity = Column(Float)
    water_h = Column(Float)
    water_cl = Column(Float)

    device = relationship('Device', back_populates='data')

# Create all tables in the database
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a scoped session factory
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

def add_user(data):
    """
    Add a new user to the database.

    Args:
        data (dict): Dictionary containing 'username', 'email', and 'password' keys.

    Returns:
        bool: True if user is successfully added, False otherwise.
    """
    session = Session()
    try:
        # Check if the username or email already exists
        if user_exists(data['username']) or user_exists(data['email']):
            return False
        
        # Create a new user object
        new_user = User(
            username=data['username'],
            email=data['email'],
            admin=False
        )
        
        # Hash and set the password
        new_user.set_password(data['password'])

        session.add(new_user)
        session.commit()
        return True
    finally:
        session.close()

def login_user(data):
    """
    Authenticate a user login based on username and password.

    Args:
        data (dict): Dictionary containing 'username' and 'password' keys.

    Returns:
        bool: True if authentication successful, False otherwise.
    """
    session = Session()
    try:
        user = session.query(User).filter_by(username=data['username']).first()
        return bool(user and user.check_password(data['password']))
    finally:
        session.close()

def user_exists(username_or_email):
    """
    Check if a user or email already exists in the database.

    Args:
        username_or_email (str): Username or email to check.

    Returns:
        bool: True if user or email exists, False otherwise.
    """
    session = Session()
    try:
        return session.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first() is not None
    finally:
        session.close()

def is_admin(user_id):
    """
    Check if a user is an admin.

    Args:
        user_id (int): User ID to check.

    Returns:
        bool: True if user is an admin, False otherwise.
    """
    session = Session()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            return user.admin
        return False
    finally:
        session.close()

def update_user_info(old_user_id, new_username, new_email, new_password):
    """
    Update user information in the database.

    Args:
        user_id (int): User ID of the user to update.
        new_username (str): New username.
        new_email (str): New email.
        new_password (str): New password (can be None to keep existing password).

    Returns:
        bool: True if update successful, False otherwise.
    """
    session = Session()
    try:
        # Retrieve the user object from the database
        user = session.query(User).filter_by(user_id=old_user_id).first()

        # If the user is not found, return False
        if not user:
            return False

        # Update user attributes
        user.username = new_username
        user.email = new_email
        
        if new_password:
            user.set_password(new_password)

        # Flush the changes to ensure the new username is updated in the user table
        session.flush()
        
        session.commit()
        
        return True
    except Exception as e:
        print(f"Error updating user info: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def add_device_to_db(user_id, device_id, device_name, latitude, longitude):
    """
    Add a new device to the database.

    Args:
        user_id (int): User ID associated with the device.
        device_id (str): Unique identifier for the device.
        device_name (str): Name of the device.

    Returns:
        bool: True if device added successfully, False otherwise.
    """
    session = Session()
    try:
        if device_exists(device_id, device_name):
            return False
        
        new_device = Device(
            device_id=device_id,
            user_id=user_id,
            device_name=device_name,
            latitude=latitude,
            longitude=longitude
        )
        
        session.add(new_device)
        
        session.commit()
        return True
    finally:
        session.close()

def update_device_to_db(old_device_id, new_user_id, new_device_id, new_device_name, new_latitude, new_longitude):
    """
    update device information to the database.

    Args:
        user_id (int): User ID associated with the device.
        device_id (str): Unique identifier for the device.
        device_name (str): Name of the device.

    Returns:
        bool: True if device added successfully, False otherwise.
    """
    session = Session()
    try:
        device = session.query(Device).filter_by(device_id=old_device_id).first()
        if not device:
            return False
        
        
        device.device_id=new_device_id,
        device.user_id=new_user_id,
        device.device_name=new_device_name,
        device.latitude=new_latitude
        device.longitude=new_longitude
        
        # Flush the changes to ensure the new username is updated in the user table
        session.flush()

        session.commit()
        return True
    finally:
        session.close()

def device_exists(device_id, device_name):
    """
    Check if a device already exists in the database.

    Args:
        device_id (str): Unique identifier for the device.
        device_name (str): Name of the device.

    Returns:
        bool: True if device exists, False otherwise.
    """
    session = Session()
    try:
        return session.query(Device).filter(or_(
            Device.device_id == device_id, Device.device_name == device_name
            )).first() is not None
    finally:
        session.close()

def delete_device_by_id(device_id):
    """
    Delete a device by its ID from the database.

    Args:
        device_id (str): Unique identifier for the device.

    Returns:
        bool: True if device deleted successfully, False otherwise.
    """
    session = Session()
    try:
        device = session.query(Device).filter_by(device_id=device_id).first()
        if device:
            session.delete(device)
            session.commit()
            return True
        return False
    except Exception as e:
        print(f"Error deleting device: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def get_all_devices():
    """
    Retrieve all devices from the database.

    Returns:
        list: List of Device objects representing all devices in the database.
    """
    session = Session()
    try:
        return session.query(Device).order_by(Device.device_name).all()
    finally:
        session.close()

def get_all_users():
    """
    Retrieve all users from the database.

    Returns:
        list: List of User objects representing all users in the database.
    """
    session = Session()
    try:
        return session.query(User).order_by(User.username).all()
    finally:
        session.close()

def get_user_id(username):
    """
    Retrieve user ID by username from the database.

    Args:
        username (str): Username of the user to retrieve ID for.

    Returns:
        int: User ID of the specified user.
    """
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        return user.user_id
    finally:
        session.close()

def get_user_info(user_id):
    """
    Retrieve user information by user ID from the database.

    Args:
        user_id (int): User ID of the user to retrieve information for.

    Returns:
        User: User object representing the user information.
    """
    session = Session()
    try:
        return session.query(User).filter_by(user_id=user_id).first()
    finally:
        session.close()

def get_user_devices(user_id):
    """
    Retrieve devices associated with a specific user from the database.

    Args:
        user_id (int): User ID of the user whose devices to retrieve.

    Returns:
        list: List of Device objects associated with the user.
    """
    session = Session()
    try:
        return session.query(Device).filter_by(user_id=user_id).order_by(Device.device_name).all()
    finally:
        session.close()

def get_device_data(device_id):
    """
    Retrieve data entries for a specific device from the database.

    Args:
        device_id (str): Unique identifier for the device.

    Returns:
        list: List of Data objects representing data entries for the device.
    """
    session = Session()
    try:
        return session.query(Data).filter_by(device_id=device_id).order_by(desc(Data.time)).all()
    finally:
        session.close()

def get_device_last_data(device_id):
    """
    Retrieve the most recent data entry for a specific device from the database.

    Args:
        device_id (str): Unique identifier for the device.

    Returns:
        Data: Data object representing the most recent data entry for the device.
    """
    session = Session()
    try:
        return session.query(Data).filter_by(device_id=device_id).order_by(desc(Data.time)).first()
    finally:
        session.close()

def get_device_info(device_id):
    """
    Retrieve device information by its ID from the database.

    Args:
        device_id (str): Unique identifier for the device.

    Returns:
        Device: Device object representing the device information.
    """
    session = Session()
    try:
        return session.query(Device).filter_by(device_id=device_id).first()
    finally:
        session.close()

def get_data_by_device_and_time(device_id, time_range):
    """
    Retrieve data entries for a device within a specified time range from the database.

    Args:
        device_id (str): Unique identifier for the device.
        time_range (str): Time range identifier ('today', '24_hours', 'this_week', 'one_week', 'all_time').

    Returns:
        str: JSON-encoded string representing data entries within the specified time range.
    """
    session = Session()
    try:
        # Determine the start time based on the specified time range
        if time_range == 'today':
            start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
        elif time_range == '24_hours':
            start_time = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        elif time_range == 'this_week':
            start_time = (datetime.now() - timedelta(days=datetime.now().weekday())).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
        elif time_range == 'one_week':
            start_time = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S')
        elif time_range == 'all_time':
            start_time = datetime.min.strftime('%Y-%m-%d %H:%M:%S')  # Set to a very old date
        else:
            start_time = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Query data from the database based on the device ID and time range
        data_objects = session.query(Data).filter(
            Data.device_id == device_id,
            Data.time >= start_time
        ).order_by(Data.time).all()
        
        # Initialize an empty list to store dictionaries
        data_dicts = []
        
        # Convert data objects to dictionaries
        for data_obj in data_objects:
            data_dict = {
                'time': data_obj.time.strftime('%Y-%m-%d %H:%M:%S'),
                'temp': data_obj.temp,
                'ph': data_obj.ph,
                'tds': data_obj.tds,
                'do': data_obj.do,
                'orp': data_obj.orp,
                'salinity': data_obj.salinity,
                'water_h': data_obj.water_h,
                'water_cl': data_obj.water_cl
            }
            data_dicts.append(data_dict)
        
        # Serialize to JSON
        return json.dumps(data_dicts)
    finally:
        session.close()

def get_data(device_id, start_date=None, end_date=None):
    """
    Fetch stored data for a device within a specified date range.

    Args:
        device_id (str): Unique identifier for the device.
        start_date (str, optional): Start date for the data range in the format 'YYYY-MM-DD'.
        end_date (str, optional): End date for the data range in the format 'YYYY-MM-DD'.

    Returns:
        list: List of dictionaries containing device data.
    """
    session = Session()
    try:
        query = session.query(Data).filter(Data.device_id == device_id)
        
        if start_date:
            query = query.filter(Data.time >= datetime.strptime(start_date, "%Y-%m-%d"))
        
        if end_date:
            query = query.filter(Data.time <= datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1))
        
        data_entries = query.order_by(desc(Data.time)).all()
        
        return [
            {
                "time": data.time.strftime("%Y-%m-%d %H:%M:%S"),
                "temp": data.temp,
                "ph": data.ph,
                "tds": data.tds,
                "do": data.do,
                "orp": data.orp,
                "salinity": data.salinity,
                "water_h": data.water_h,
                "water_cl": data.water_cl
            }
            for data in data_entries
        ]
    finally:
        session.close()

def store_data(device_id):
    """
    Fetch and store data from an external API to the database.

    Args:
        device_id (str): Unique identifier for the device.
    """
    session = Session()
    try:
        # Retrieve device name and last recorded time from the database
        device_name = get_device_info(device_id=device_id).device_name
        try:
            last_time = get_device_last_data(device_id=device_id).time
        except AttributeError:
            last_time = datetime(1970, 1, 1)
        
        # Define the URL and headers for the external API
        url = f"https://platform.antares.id:8443/~/antares-cse/antares-id/{app_lora}/{device_name}?fu=1&drt=2&ty=4"
        headers = {
            "X-M2M-Origin": f"{api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Fetch data from the API
        json_array = fetch_data_api_antares(device_id, url, headers, last_time)

        # Iterate over fetched data and add to the database
        for entry in json_array:
            new_data = Data(
                device_id=entry['device_id'],
                time=entry['time'],
                temp=entry['temp'],
                ph=entry['ph'],
                tds=entry['tds'],
                do=entry['do'],
                orp=entry['orp'],
                salinity=entry['salinity'],
                water_h=entry['water_h'],
                water_cl=entry['water_cl']
            )
            session.add(new_data)

        # Commit the changes to the database
        try:
            session.commit()
        except IntegrityError as e:
            session.rollback()
            print(f"Error inserting data: {e}")
    finally:
        session.close()
