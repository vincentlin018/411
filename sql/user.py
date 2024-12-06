from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import hashlib
import bcrypt

Base = declarative_base()
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    username = Column(String, unique = True, nullable = False)
    salt = Column(String, nullable = False)
    hashed_password = Column(String, nullable = False)

engine = create_engine('sqlite:///users.db')

Base.metadata.create_all(engine)

Session = sessionmaker(bind = engine)
session = Session()

def add_user(username, password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    new_user = User(username = username, salt = salt.hex(), hashed_password = hashed_password.hex())

    session.add(new_user)
    session.commit()

def check_password(username, password):
    user = session.query(User).filter_by(username = username).first()
    if user and bcrypt.checkpw(password.encode(), bytes.fromhex(user.hashed_password)):
        return True
    return False