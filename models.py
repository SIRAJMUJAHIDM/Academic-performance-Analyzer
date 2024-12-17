from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer
from database import base,db_engine
from fastapi import FastAPI, UploadFile, File
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker


class Batch(base):
    __tablename__ = "batch"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(String(30))
    batch = Column(String(30))
    class_incharge = Column(String(30))
    tutor1=Column(String(30))
    tutor2=Column(String(30))
    tutor3=Column(String(30))
    no_of_students = Column(String(30))

class Subject(base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    subject_Code = Column(String(30))
    Subject_Name=Column(String(30))
    semester=Column(String(30))
    credits = Column(String(30))

class Faculty(base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30)) 
    email=Column(String(30)) 
    designation=Column(String(30)) 
    password = Column(String(30))

class StudentData:
    def __init__(self, s_no: int, register_no: str, name: str, **subjects):
        self.s_no = s_no
        self.register_no = register_no
        self.name = name
        for subject, grade in subjects.items():
            setattr(self, subject, grade)
    
# create table registeration ( id int AUTO_INCREMENT PRIMARY KEY,name varchar(30) NOT NULL,dob int NOT NULL,mail_id varchar(30) NOT NULL,father_name varchar(30) NOT NULL,mother_name varchar(30) NOT NULL,gender varchar(30) NOT NULL,category varchar(30) NOT NULL);
base.metadata.create_all(bind=db_engine)
