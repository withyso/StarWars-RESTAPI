from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return 'Usuario con email: {}'.format(self.email)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            'is_active': self.is_active,
            # do not serialize the password, its a security breach
        }

class Planets(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    population = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Planet {self.id} {self.name}'
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
        }
    
class Characters(db.Model):
    __tablename__ = "characters"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    height = db.Column(db.Integer, nullable=False)
    mass = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return f'Character ID: {self.id} Name: {self.name}'
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "Mass": self.mass,
            "gender": self.gender,
        }
    def serialize_prev(self):
        return{
            "id": self.id,
            "name": self.name,
        }
