from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    atmosphere = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "atmosphere": self.atmosphere,
        }


class Characters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(300), nullable=False)
    hair_color = db.Column(db.String(30), nullable=True)
    eye_color = db.Column(db.String(30), nullable=True)

    def __repr__(self):
        return self.full_name

    def serialize(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
        }


class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship(User)

    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), nullable=True)
    character = db.relationship(Characters)

    planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"), nullable=True)
    planet = db.relationship(Planets)

    def __repr__(self):
        return f"User {self.use_id} favorites"

    def serialize(self):
        return {
            "user_id": self.user_id,
            "character_id": self.character_id if self.character_id else None,
            "character": self.character if self.character else None,
            "planet_id": self.planet_id if self.planet_id else None,
            "planet": self.planet if self.planet else None,
        }
