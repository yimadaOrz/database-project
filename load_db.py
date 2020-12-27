import psycopg2
import pandas as pd
from dotenv import find_dotenv, load_dotenv
import os

# find .env automagically by walking up directories until it's found, then
# load up the .env entries as environment variables
load_dotenv(load_dotenv())
dbname = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

conn = psycopg2.connect(host='postgres',
                       port='5432',
                       dbname=dbname,
                       user=user,
                       password=password
                        )

cur = conn.cursor()

# creating table
# cur.execute("drop table if exists userstable;")
cur.execute("""
drop table if exists Fields cascade;
drop table if exists Courses cascade;
drop table if exists userstable cascade;
drop table if exists Videos cascade;
drop table if exists subjects cascade;
drop table if exists lessons cascade;
drop table if exists records cascade;
drop table if exists questions cascade;

create table fields(
    FieldID varchar(128)  primary key,
    FieldName varchar(128)
);

create table subjects(
    SubjectID varchar(128)  primary key,
    SubjectName varchar(128),
    FieldID varchar(128)  not null,
    foreign key (FieldID) references Fields(FieldID)
);

create table Courses(
    CourseID varchar(128) primary key,
    CourseName varchar(128),
    subjectID varchar(128) not null,
    foreign key (subjectID) references subjects(subjectID)
);

create table Lessons(
    LessonID varchar(128) primary key,
    LessonName varchar(128),
    CourseID varchar(128) not null,
    foreign key (CourseID) references Courses(CourseID)
);

create table questions(
    questionID serial primary key,
    question varchar(1024),
    answer varchar(128),
    lessonid varchar(128) not null,
    foreign key (LessonID) references Lessons(LessonID)
);

create table Videos(
    VideoID varchar(128) primary key,
    VideoName varchar(128),
    videolink varchar(128),
    lessonid varchar(128) not null,
    foreign key (LessonID) references Lessons(LessonID)
);

create table userstable(
    username varchar(128) primary key,
    password varchar(128)
);

create table records(
    recordid serial primary key,
    username varchar(128) not null,
    ftime date,
    LessonID varchar(128) not null,
    foreign key (LessonID) references Lessons(LessonID),
    foreign key (username) references userstable(username)
);""")
conn.commit()
print("table created")
print(os.getcwd)



conn.commit()
# loading data into table
with open('userstable.csv', 'r') as f:
    next(f)    # skip headers
    cur.copy_from(f, 'userstable', sep=',')
conn.commit()
print("loaded data into userstable table")

with open('fields.csv', 'r') as f:
    next(f)    # skip headers
    cur.copy_from(f, 'fields', sep=',')
conn.commit()
print("loaded data into fields table")

with open('subjects.csv', 'r') as f:
    next(f)    # skip headers
    cur.copy_from(f, 'subjects', sep=',')
conn.commit()
print("loaded data into subjects table")

cur.copy_expert("""COPY Courses from STDIN CSV HEADER""", open('./courses.csv'),)
conn.commit()
print('loaded data into Courses table')

cur.copy_expert("""COPY lessons from STDIN CSV HEADER""", open('./lessons.csv'),)
conn.commit()
print('loaded data into lessons table')

cur.copy_expert("""COPY questions from STDIN CSV HEADER""", open('./questions.csv'),)
conn.commit()
print('loaded data into questions table')

cur.copy_expert("""COPY videos from STDIN CSV HEADER""", open('./videos.csv'),)
conn.commit()
print('loaded data into Videos table')

cur.copy_expert("""COPY records from STDIN CSV HEADER""", open('./records.csv'),)
conn.commit()
print('loaded data into records table')

# with open('records.csv', 'r') as f:
#     next(f)    # skip headers
#     cur.copy_from(f, 'records', sep=',')
# conn.commit()
# print("loaded data into records table")