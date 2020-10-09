from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import json

app = Flask(__name__)
dbURL = 'mysql+mysqlconnector://root@db:3306/ja'  # For Docker
dbURL = 'mysql+mysqlconnector://root@localhost:3306/ja'  # For local
app.config['SQLALCHEMY_DATABASE_URI'] = dbURL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    contact_no = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    school = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    language = db.Column(db.String(20), nullable=False)

    def json(self):
        return {
            'student_id': self.student_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'contact_no': self.contact_no,
            'email': self.email,
            'school': self.school,
            'age': self.age,
            'gender': self.gender,
            'language': self.language
        }


class Volunteer(db.Model):
    __tablename__ = 'volunteer'
    volunteer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    contact_no = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(80), nullable=False)
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
            'volunteer_id': self.volunteer_id,
            'category': self.category,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'contact_no': self.contact_no,
            'email': self.email,
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


engine = create_engine(dbURL)
if not database_exists(engine.url):
    create_database(engine.url)
db.create_all()
db.session.commit()


@app.route("/students/all", methods=['GET'])
def getallstudents():
    return {'students': [student.json() for student in Student.query.all()]}


@app.route("/students/find", methods=['GET'])
def getstudent():
    student_id = request.args.get('student_id')
    return Student.query.filter_by(student_id=student_id).first().json()


@app.route("/students/update", methods=['POST'])
def newstudent():
    data = request.form.to_dict()
    db.session.merge(Student(**data))
    db.session.commit()
    return "OK", 200


@app.route("/volunteers/all", methods=['GET'])
def getallvolunteers():
    return {'volunteers': [volunteer.json() for volunteer in Volunteer.query.all()]}


@app.route("/volunteers/find", methods=['GET'])
def getvolunteer():
    volunteer_id = request.args.get('volunteer_id')
    return Volunteer.query.filter_by(volunteer_id=volunteer_id).first().json()


@app.route("/volunteers/update", methods=['POST'])
def newvolunteer():
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
def newprogram():
    data = request.form.to_dict()
    db.session.merge(Program(**data))
    db.session.commit()
    return "OK", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
