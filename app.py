from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os

dbdir="sqlite:///" + os.path.abspath(os.getcwd()) + "/database.db"

UPLOAD_FOLDER = os.path.abspath("./uploads/")


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"]=dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False # para evitar notidicaciones 
db=SQLAlchemy(app)

#clases para el ORM que mapean a las tablas
class Docente(db.Model):
	dniDocente=db.Column(db.Integer, primary_key=True)
	nombre=db.Column(db.String(50), nullable=False)
	apePaterno=db.Column(db.String(50),nullable=False)
	apeMaterno=db.Column(db.String(50),nullable=False)
	contrasenia=db.Column(db.String(80), nullable=False)
	cursos=db.relationship('Curso', backref='docente', lazy=True)#esto es para que desde la lista de cursos se acceda a los campos de Docente

class Estudiante(db.Model):
	dniEstudiante=db.Column(db.Integer, primary_key=True)
	nombre=db.Column(db.String(50), nullable=False)
	apePaterno=db.Column(db.String(50), nullable=False)
	apeMaterno=db.Column(db.String(50), nullable=False)
	contrasenia=db.Column(db.String(80), nullable=False)
	subcripciones=db.relationship('Subcripcion', backref='estudiante',lazy=True)

class Curso(db.Model):
	idCurso=db.Column(db.Integer, primary_key=True, autoincrement=True)
	categoria=db.Column(db.String(50), nullable=False)
	nombre=db.Column(db.String(50), nullable=False)
	dniDocente=db.Column(db.Integer, db.ForeignKey('docente.dniDocente'))#docente hace refenrencia ala tabla que es creada por la clase Docente que por convencion su tabla esta en minisculas
	sesiones=db.relationship('Sesion', backref='curso', lazy=True)

class Sesion(db.Model):
	idSesion=db.Column(db.Integer, primary_key=True, autoincrement=True)
	numSesion=db.Column(db.Integer, nullable=False)
	titulo=db.Column(db.String(50), nullable=False)
	contenido=db.Column(db.String(50))
	material=db.Column(db.LargeBinary)
	idCurso=db.Column(db.Integer, db.ForeignKey('curso.idCurso'))
	videos=db.relationship('Video',backref='sesion',lazy=True)

class Video(db.Model):
	idVideo=db.Column(db.Integer, primary_key=True, autoincrement=True)
	nombre=db.Column(db.String(50), nullable=False)
	idSesion=db.Column(db.Integer, db.ForeignKey('sesion.idSesion'))

class Subcripcion(db.Model):
	idSubcripcion=db.Column(db.Integer, primary_key=True, autoincrement=True)
	dniEstudiante=db.Column(db.Integer, db.ForeignKey('estudiante.dniEstudiante'))
	idCurso=db.Column(db.Integer, db.ForeignKey('curso.idCurso'))

with app.app_context():# Ahora se neseita el contexto para crear la base de datos por defecto
    db.create_all()

@app.route("/")
def index():
	return render_template('index.html')

@app.route("/ver/<filename>")
def get_file(filename):
	
	return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

##la carnecita esta arriba

#listar docentes
@app.route("/docentes", methods=["GET"])
def docentes():
	docQuery=Docente.query.all()

	for doc in docQuery:
		print(doc.dniDocente)
	return render_template("docentes.html", docentes=docQuery)
#registro docente
@app.route("/regDocente", methods=["GET","POST"])
def reg_docente():
	if request.method == 'POST':
		dniB = request.form["dniT"]
		nombreB = request.form["nombreT"]
		apePaternoB = request.form["apePaternoT"]
		apeMaternoB = request.form["apeMaternoT"]
		hashed_pw = generate_password_hash(request.form["contraseniaT"],method="sha256")
		new_docente = Docente(dniDocente=dniB, nombre=nombreB, apePaterno=apePaternoB,apeMaterno=apeMaternoB, contrasenia=hashed_pw)
		db.session.add(new_docente)
		db.session.commit()
		return redirect("docentes")
	return render_template("docente.html")


if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0")