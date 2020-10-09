from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *
import json
import os

app = Flask(__name__)
dbURL = os.getenv('DOCKERDB')
if not dbURL:  # for local testing
    dbURL = 'mysql+mysqlconnector://root@localhost:3306/ja'
app.config['SQLALCHEMY_DATABASE_URI'] = dbURL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)


class User(db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String(80), primary_key=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __init__(self, username, password, role):
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
        self.role = role

    def check(self, password):
        return {bcrypt.check_password_hash(self.password, password)}


class Student(db.Model):
    __tablename__ = 'student'
    email = db.Column(db.String(80), primary_key=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    contact_no = db.Column(db.String(20), nullable=False)
    school = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    language = db.Column(db.String(20), nullable=False)

    def json(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'contact_no': self.contact_no,
            'school': self.school,
            'age': self.age,
            'gender': self.gender,
            'language': self.language
        }

@event.listens_for(Student.__table__, 'after_create')
def create_students(*args, **kwargs):
    db.session.add(Student(email='abc@xyz.gmail.com', first_name='test first name', last_name="test last name", contact_no="12345678", school="HKU", age=21, gender="Male",language="Cantonese"))
    db.session.add(Student(email='bla@bla.yahoo.com', first_name='test 1', last_name="test 2", contact_no="12345678", school="CUHK", age=23, gender="Male", language="Cantonese, English"))
    db.session.commit()


class Volunteer(db.Model):
    __tablename__ = 'volunteer'
    email = db.Column(db.String(80), primary_key=True, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    contact_no = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    language = db.Column(db.String(20), nullable=False)
    company = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(80), nullable=False)
    education_level = db.Column(db.String(80), nullable=False)
    years_of_working_experience = db.Column(db.Integer, nullable=False)
    preferred_timing = db.Column(db.String(80), nullable=False)
    preferred_student_group = db.Column(db.String(80), nullable=False)

    def json(self):
        return {
            'email': self.email,
            'category': self.category,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'contact_no': self.contact_no,
            'age': self.age,
            'gender': self.gender,
            'language': self.language,
            'company': self.company,
            'position': self.position,
            'education_level': self.education_level,
            'years_of_working_experience': self.years_of_working_experience,
            'preferred_timing': self.preferred_student_group,
            'preferred_student_group': self.preferred_student_group
        }


class Program(db.Model):
    __tablename__ = 'program'
    program_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    program_type = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    start_date = db.Column(db.String(80), nullable=False)
    end_date = db.Column(db.String(80), nullable=False)
    host = db.Column(db.String(80), nullable=False)
    ratio = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    program_format = db.Column(db.String(80), nullable=False)

    def json(self):
        return {
            'program_id': self.program_id,
            'program_type': self.program_type,
            'name': self.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'host': self.host,
            'ratio': self.ratio,
            'capacity': self.capacity,
            'program_format': self.program_format
        }


class StudentLink(db.Model):
    __tablename__ = "student_link"
    student_id = db.Column(db.Integer, ForeignKey(
        "student.student_id"), primary_key=True, nullable=False)
    program_id = db.Column(db.Integer, ForeignKey(
        "program.program_id"), primary_key=True, nullable=False)

    def json(self):
        return {
            "student_id": self.student_id,
            "program_id": self.program_id
        }


class VolunteerLink(db.Model):
    __tablename__ = "volunteer_link"
    volunteer_id = db.Column(db.Integer, ForeignKey(
        "volunteer.volunteer_id"), primary_key=True, nullable=False)
    program_id = db.Column(db.Integer, ForeignKey(
        "program.program_id"), primary_key=True, nullable=False)

    def json(self):
        return {
            "volunteer_id": self.volunteer_id,
            "program_id": self.program_id
        }


engine = create_engine(dbURL)
if not database_exists(engine.url):
    create_database(engine.url)
db.create_all()
db.session.commit()


@app.route("/login", methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        user = User.query.filter_by(username=username).first()
        if user.check(password):
            return user.role, 200
        else:
            raise ValueError
    except:
        return "Unauthorised", 403


@app.route("/register", methods=['POST'])
def register():
    data = request.form.to_dict()
    db.session.add(User(**data))
    db.session.commit()
    return "OK", 200


@app.route("/students/all", methods=['GET'])
def get_all_students():
    return {'students': [student.json() for student in Student.query.all()]}


@app.route("/students/find", methods=['GET'])
def get_student_by_email():
    student_email = request.args.get('student_email')
    return Student.query.filter_by(student_email=student_email).first().json()


@app.route("/students/update", methods=['POST'])
def new_student():
    data = request.form.to_dict()
    db.session.merge(Student(**data))
    db.session.commit()
    return "OK", 200

@app.route("/students/register", methods=['POST'])
def register_student():
    data = request.form.to_dict()
    db.session.merge(Student(**data))
    db.session.commit()
    return "OK", 200

@app.route("/volunteers/all", methods=['GET'])
def get_all_volunteers():
    return {'volunteers': [volunteer.json() for volunteer in Volunteer.query.all()]}


@app.route("/volunteers/find", methods=['GET'])
def get_volunteer_by_email():
    volunteer_email = request.args.get('volunteer_email')
    return Volunteer.query.filter_by(volunteer_email=volunteer_email).first().json()


@app.route("/volunteers/update", methods=['POST'])
def new_volunteer():
    data = request.form.to_dict()
    db.session.merge(Volunteer(**data))
    db.session.commit()
    return "OK", 200

@app.route("/volunteers/register", methods=['POST'])
def register_volunteer():
    data = request.form.to_dict()
    db.session.merge(Volunteer(**data))
    db.session.commit()
    return "OK", 200

@app.route("/programs/all", methods=['GET'])
def get_all_programs():
    return {'programs': [program.json() for program in Program.query.all()]}


@app.route("/programs/find", methods=['GET'])
def get_program_by_id():
    program_id = request.args.get('program_id')
    return Program.query.filter_by(program_id=program_id).first().json()


@app.route("/programs/update", methods=['POST'])
def new_program():
    data = request.form.to_dict()
    db.session.merge(Program(**data))
    db.session.commit()
    return "OK", 200


@app.route("/programs/attendees", methods=['GET'])
def get_attendees_by_id():
    program_id = request.args.get('program_id')
    students = [student.json() for student in StudentLink.query.filter_by(
        program_id=program_id).all()]
    volunteers = [volunteer.json() for volunteer in VolunteerLink.query.filter_by(
        program_id=program_id).all()]
    return {
        'students': students,
        'volunteers': volunteers,
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
