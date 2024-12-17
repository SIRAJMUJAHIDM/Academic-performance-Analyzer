from fastapi import FastAPI,Request,Depends,Form,UploadFile, File,HTTPException
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table,text,select, column
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse,JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
from sqlalchemy import inspect
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
# from models import base
import re
import models
import pandas as pd
from database import db_engine as engine
from io import BytesIO



metadata = MetaData()
app=FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount("/templates/static",StaticFiles(directory="templates/static"), name="static")

def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.get('/student') 
def get_form(request:Request,db:Session = Depends(get_db)):
    
    return templates.TemplateResponse("/tutor.html", context={"request": request})



#cGet The Template
@app.get('/staff') 
def get_form(request:Request,db:Session = Depends(get_db)):
    batches = db.query(models.Batch).all()  # Fetch all batches from the database
    batches.reverse()
    return templates.TemplateResponse("/sample.html", context={"request": request, "batches": batches})




@app.post('/batch') 
def get_form(
    request: Request,
    db: Session = Depends(get_db),
    year: str = Form(...),
    batch: str = Form(...),
    incharge: str = Form(...),
    tutor1: str = Form(...),
    tutor2: str = Form(...),
    tutor3: str = Form(...),
    numberOfStudents: str = Form(...),
):
    new_batch = models.Batch(
        year=year,
        batch=batch,
        class_incharge=incharge,
        tutor1=tutor1,
        tutor2=tutor2,
        tutor3=tutor3,
        no_of_students=numberOfStudents,
    )
    # Add the new batch to the database
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    error = "Done"
    json_compatible_item_data = jsonable_encoder(error)
    return JSONResponse(content=json_compatible_item_data)


def table_exists(table_name):
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

# Function to create a table from DataFrame column names
def create_table_from_dataframe(column_names, table_name, metadata, engine):
    inspector = inspect(engine)
    if inspector.has_table(table_name):
        print(f"Table '{table_name}' already exists. Skipping table creation.")
        return
    
    table_columns = [
        Column(col_name.replace(' ', '_').upper(), String(length=255)) for col_name in column_names
    ]

    table = Table(table_name, metadata, *table_columns)
    metadata.create_all(engine)

    print(f"Table '{table_name}' created successfully.")


# Upload endpoint to process Excel files and insert data into the database
@app.post("/upload/")
async def upload_excel(file: UploadFile = File(...),batch: str = Form(...), semester: str = Form(...)):
    if file.filename.endswith(".xlsx"):
        contents = await file.read()
        print("Batch:", batch)
        print("Semester:", semester)
        print("File Name:", file.filename)
        
        
        # Use BytesIO to wrap the byte string
        contents_io = BytesIO(contents)
        
        df = pd.read_excel(contents_io)
        df.columns = df.columns.str.replace(' ', '_').str.lower()
        
        # Generate table name from batch and semester
        table_name = f"{batch}_{semester}"
        
        if not table_exists(table_name):
            create_table_from_dataframe(df.columns.tolist(), table_name, metadata, engine)
        
        # Insert data into the table
        df.to_sql(table_name, engine, if_exists='append', index=False)

        return JSONResponse(content={"success": True, "message": "Data uploaded successfully."})
    else:
        return JSONResponse(content={"success": False, "message": "Only Excel files (.xlsx) are allowed."})
    
    
@app.get('/faculty') 
def get_form(request:Request,db:Session = Depends(get_db)):
    faculties = db.query(models.Faculty).all() 
    return templates.TemplateResponse("/faculty.html", context={"request": request,"faculties": faculties})

@app.post("/add_faculty/")
def add_faculty(request:Request,username: str = Form(...), email: str = Form(...), designation: str = Form(...), password: str = Form(...), db:Session = Depends(get_db)):
    # Create a new faculty instance
    new_faculty = models.Faculty(name=username, email=email, designation=designation, password=password)

    # Add the new faculty to the database session
    db.add(new_faculty)
    db.commit()
    db.refresh(new_faculty)

    return JSONResponse(content={"success": True, "message": "Data uploaded successfully."})


# getting data for showing edit
@app.get("/get_faculty/{faculty_id}")
def get_faculty(faculty_id: int, db: Session = Depends(get_db)):
    faculty = db.query(models.Faculty).filter(models.Faculty.id == faculty_id).first()
    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculty



# update the faculty
@app.put("/update_faculty/{faculty_id}")
async def update_faculty(faculty_id: int, 
                          name: str = Form(...), 
                          email: str = Form(...), 
                          designation: str = Form(...), 
                          password: str = Form(...), 
                          db: Session = Depends(get_db)):
    
    faculty = db.query(models.Faculty).filter(models.Faculty.id == faculty_id).first()
    print(faculty.name)
    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")

    faculty.name=name
    faculty.email=email
    faculty.designation=designation
    faculty.password=password
    db.commit()

    return JSONResponse(content={"success": True, "message": "Data uploaded successfully."})

# delete Faculty

@app.delete("/delete_faculty/{faculty_id}")
def delete_faculty(faculty_id: int, db: Session = Depends(get_db)):
    faculty = db.query(models.Faculty).filter(models.Faculty.id == faculty_id).first()
    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    db.delete(faculty)
    db.commit()
    return {"message": f"Faculty with ID {faculty_id} deleted successfully"}




# Subjects& credits
@app.get('/subjects') 
def get_form(request:Request,db:Session = Depends(get_db)):
    subject = db.query(models.Subject).all() 
    return templates.TemplateResponse("/subject.html", context={"request": request,"subjects":subject  })

# subject Add
@app.post("/add_subject")
def add_subject(subject_name: str = Form(...),
                semester: str = Form(...),
                subject_code: str = Form(...),
                credits: str = Form(...),
                db: Session = Depends(get_db)):
    db_subject = models.Subject(Subject_Name=subject_name,
                                 semester=semester,
                                 subject_Code=subject_code,
                                 credits=credits)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


# get suject dor edit modal
@app.get("/get_subject/{subject_id}")
def get_faculty(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if subject is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return subject


# subject update
@app.put("/update_subject/{subject_id}")
def update_subject(subject_id: int, 
                   subjectName: str = Form(...),
                   semester: str = Form(...),
                   subjectCode: str = Form(...),
                   credits: str = Form(...),
                   db: Session = Depends(SessionLocal)):
    db_subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")

    db_subject.Subject_Name = subjectName
    db_subject.semester = semester
    db_subject.subject_Code = subjectCode
    db_subject.credits = credits

    db.commit()
    db.refresh(db_subject)
    return db_subject 

@app.delete("/delete_subject/{faculty_id}")
def delete_faculty(faculty_id: int, db: Session = Depends(get_db)):
    faculty = db.query(models.Subject).filter(models.Subject.id == faculty_id).first()
    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty not found")
    db.delete(faculty)
    db.commit()
    return {"message": f"Faculty with ID {faculty_id} deleted successfully"}