from flask import Flask, request, redirect, url_for, render_template, send_from_directory,jsonify
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

#clases para areas y categoria


class Categoria(db.Model):
	idCategoria=db.Column(db.Integer, primary_key=True,autoincrement=True)
	nombCategoria=db.Column(db.String(50),nullable=False)
	descripcion=db.Column(db.String(200))
	cursos=db.relationship('Curso', backref='categoria', lazy=True)

class Curso(db.Model):
	idCurso=db.Column(db.Integer, primary_key=True, autoincrement=True)
	nombre=db.Column(db.String(50), nullable=False)
	dniDocente=db.Column(db.Integer, db.ForeignKey('docente.dniDocente'))#docente hace refenrencia ala tabla que es creada por la clase Docente que por convencion su tabla esta en minisculas
	idCategoria=db.Column(db.Integer, db.ForeignKey('categoria.idCategoria'))
	sesiones=db.relationship('Sesion', backref='curso', lazy=True)

class Sesion(db.Model):
	idSesion=db.Column(db.Integer, primary_key=True, autoincrement=True)
	numSesion=db.Column(db.Integer, nullable=False)
	titulo=db.Column(db.String(50), nullable=False)
	contenido=db.Column(db.String(300))
	material=db.Column(db.LargeBinary)
	idCurso=db.Column(db.Integer, db.ForeignKey('curso.idCurso'))
	videos=db.relationship('Video',backref='sesion',lazy=True)

class Video(db.Model):
	idVideo=db.Column(db.Integer, primary_key=True, autoincrement=True)
	nombre=db.Column(db.String(50), nullable=False)
	idSesion=db.Column(db.Integer, db.ForeignKey('sesion.idSesion'), unique=True)

class Subcripcion(db.Model):
	idSubcripcion=db.Column(db.Integer, primary_key=True, autoincrement=True)
	dniEstudiante=db.Column(db.Integer, db.ForeignKey('estudiante.dniEstudiante'))
	idCurso=db.Column(db.Integer, db.ForeignKey('curso.idCurso'))



@app.route("/")
def index():
	return render_template('index.html')

@app.route("/ver/<filename>")
def get_file(filename):
	
	return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

##la carnecita esta arriba

#listar docentes
@app.route("/docentes", methods=["GET"])
def list_docentes():
	docQuery=Docente.query.all()

	for doc in docQuery:
		print(doc.dniDocente)
	return render_template("docentes.html", docentes=docQuery)
#registro docente
@app.route("/regdocente", methods=["GET","POST"])
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

#actualizar docente
@app.route("/updocente/<int:dni>", methods=["POST"])
def up_docente(dni):
	docente = Docente.query.get(dni)
	if docente is None:
		return "no se encuentra el docente indicado"
	docente.nombre = request.form["nombreT"]
	docente.apePaterno = request.form["apePaternoT"]
	docente.apeMaterno = request.form["apeMaternoT"]
	docente.contrasenia = generate_password_hash(request.form["contraseniaT"],method="sha256")
	db.session.commit()
	return redirect(url_for('list_docentes'))

#emiminar docente
@app.route("/deldocente/<int:dni>", methods=["POST"])
def del_docente(dni):
	docQuery=Docente.query.get(dni)
	if docQuery is None:
		"No exite el docente"
	db.session.delete(docQuery)
	db.session.commit()
	return redirect(url_for('list_docentes'))


#listar estudiantes
@app.route("/regestudiante", methods=["GET","POST"])
def reg_estudiante():
	if request.method == 'POST':
		dniB = request.form["dniT"]
		nombreB = request.form["nombreT"]
		apePaternoB = request.form["apePaternoT"]
		apeMaternoB = request.form["apeMaternoT"]
		hashed_pw = generate_password_hash(request.form["contraseniaT"],method="sha256")
		new_estudiante = Estudiante(dniEstudiante=dniB, nombre=nombreB, apePaterno=apePaternoB,apeMaterno=apeMaternoB, contrasenia=hashed_pw)
		db.session.add(new_estudiante)
		db.session.commit()
		return redirect(url_for('list_estudiantes'))#si no esta logueado debe ir a login o loquearse automaticamnte y abrir el inicio
	return render_template("estudiante.html")

@app.route("/estudiantes", methods=["GET"])
def list_estudiantes():
	estQuery = Estudiante.query.all()
	return render_template("estudiantes.html", estudiantes=estQuery)

@app.route("/upestudiante/<int:dni>", methods=["POST"])
def up_estudiante(dni):
	estudiante= Estudiante.query.get(dni)
	if estudiante is None:
		"dni No Encontrado"
	estudiante.nombre = request.form["nombreT"]
	estudiante.apePaterno = request.form["apePaternoT"]
	estudiante.apeMaterno = request.form["apeMaternoT"]
	estudiante.contrasenia = generate_password_hash(request.form["contraseniaT"],method="sha256")
	db.session.commit()
	return redirect(url_for('list_estudiantes'))

@app.route("/delestudiante/<int:dni>", methods=["POST"])
def del_estudiante(dni):
	estQuery=Estudiante.query.get(dni)
	if estQuery is None:
		"No exite el docente"
	db.session.delete(estQuery)
	db.session.commit()
	return redirect(url_for('list_estudiantes'))

#metodos para cursos
@app.route("/cursos/<int:dni>", methods=["GET"])
def listar_curso(dni):
	dniB=dni
	curQuery = Curso.query.filter_by(dniDocente=dniB).all()
	print(curQuery)
	categoria = Categoria.query.all()
	print(categoria)
	if curQuery is None:
		"No exite Cursos con este dni"
	return render_template("cursos.html", cursos=curQuery,dni=dniB,categoriaList=categoria)

@app.route("/regcursos", methods=["GET","POST"])
def reg_curso():
	categoriaB=request.form.get('categoriaT')
	print(categoriaB)
	nombreB = request.form["nombreT"]
	dniB=request.form["dniDocenteT"]
	new_curso = Curso(nombre=nombreB, idCategoria=categoriaB,dniDocente=dniB )
	db.session.add(new_curso)
	db.session.commit()
	return redirect(url_for('listar_curso', dni=dniB))
@app.route("/upcursos", methods=["POST"])
def up_curso():
	curso = Curso.query.get(request.form["idCursoT"])
	if curso is None:
		"No se encuentra el curso"
	curso.nombre = request.form["nombreT"]
	curso.categoria = request.form["categoriaT"]
	db.session.commit()
	return redirect(url_for('listar_curso', dni=curso.dniDocente))
@app.route("/delcursos/<int:id>", methods=["POST"])
def del_cursos(id):
	curso = Curso.query.get(id)
	if curso is None:
		"No se encuentra el curso"
	db.session.delete(curso)
	db.session.commit()
	return redirect(url_for('listar_curso', dni=curso.dniDocente))

#methodos para seciones
@app.route("/listseciones/<int:idcurso>", methods=["GET"])
def listar_seciones(idcurso):
	seionQuery = Sesion.query.filter_by(idCurso=idcurso).all()
	return render_template("sesiones.html", sesiones=seionQuery,idcursoT=idcurso)

@app.route("/regseciones",methods=["POST"])
def reg_seciones():
	#registrar la seccion y luego hacer el metodo para guardar el video
	numSecion = request.form["numSesionT"]#usa ajax con vuejs para traer el numero de secciones
	titulo=request.form["tituloT"]
	contenido=request.form["contenidoT"]
	print("Num Seccion:{}".format(numSecion))
	print("El titulo:{}".format(titulo))
	print("El Contenido:{}".format(contenido))
	if "fileSesion" not in request.files:
		return "el formulario no tienen el archivo"
	archivo=request.files["fileSesion"]
	print("El Contenido:{}".format(archivo.filename))
	print("El Contenido:{}".format(app.config["UPLOAD_FOLDER"]))	
	#if os.path.exists(directorio) and os.path.isdir(directorio):
	if archivo.filename == "":
		return "nose se ha seleccionado el archivo"
	nomSeguro=secure_filename(archivo.filename)#pone los / en _ para evitar accesos no desead ## Nota el nombre de pondra por id de secion y curso combinado
	archivo.filename="nombre_nuevo"+str(numSecion)#MODIFICAR PARA CREAR UN NUEVO NOMBRE DE ACUERDO A NOMBRE DEL CURSO Y EL ID DE SESSION
	nomSeguro=archivo.filename
	print("El Nuevo Nombre:{}".format(nomSeguro))
	archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nomSeguro)) #falta guardar los datos en base sessiones
	return "Finalizo Guardo correctamente"

#@app.route('/api/data/<int:idCurso>', methods=["GET"])
#def api_data(idCurso):
#	print("Id de curso es :"+str(idCurso))
#	data = {'message': '¡Datos desde el servidor!'}
#	return jsonify(data)

@app.route("/enumerarseciones/<int:idCurso>", methods=["GET"])
def enumerar_seciones(idCurso):
	numSecion =  Sesion.query.filter_by(idCurso=idCurso).count()
	if numSecion!=0:
		data={'numSec':numSecion+1}
		return jsonify(data)
	else:
		data={'numSec':0}
		return jsonify(data)

if __name__ == '__main__':
	with app.app_context():# Ahora se neseita el contexto para crear la base de datos por defecto
		db.create_all()
	app.run(debug=True, host="0.0.0.0")
	