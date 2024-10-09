from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # Relationship with HeroPower
    powers = relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')

    # Serialization rules to limit recursion depth
    serialize_rules = ('-powers.hero',)

    def __repr__(self):
        return f'<Hero {self.id}>'

class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # Relationship with HeroPower
    heroes = relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')

    # Serialization rules to limit recursion depth
    serialize_rules = ('-heroes.power',)

    # Validation
    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError('Name cannot be empty')
        return name

    def __repr__(self):
        return f'<Power {self.id}>'

class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # Relationships
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)

    hero = relationship('Hero', back_populates='powers')
    power = relationship('Power', back_populates='heroes')

    # Serialization rules
    serialize_rules = ('-hero.powers', '-power.heroes')

    # Validation
    @validates('strength')
    def validate_strength(self, key, strength):
        if not strength:
            raise ValueError('Strength cannot be empty')
        return strength

    def __repr__(self):
        return f'<HeroPower {self.id}>'
