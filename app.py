# local
import load_db
# 3rd party
import streamlit as st
import numpy as np
import pandas as pd
import psycopg2
import time
from dotenv import find_dotenv, load_dotenv

# built-in
import os
import base64


# find .env automagically by walking up directories until it's found, then
# load up the .env entries as environment variables
load_dotenv(load_dotenv())
dbname = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
# connect to the database
conn = psycopg2.connect(host='postgres',
                   port='5432',
                   dbname=dbname,
                   user=user,
                   password=password
                    )
# Open a cursor to perform database operations
cur = conn.cursor()

def query_db(sql: str):
    # Execute a command: this creates a new table
    cur.execute(sql)
    # Obtain data
    data = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    # Make the changes to the database persistent
    conn.commit()

    df = pd.DataFrame(data=data, columns=column_names)

    return df
# DB  Functions
def create_usertable():
    cur.execute('CREATE TABLE IF NOT EXISTS userstable(username varchar(128),password TEXT)')


def add_userdata(username,password):
    query = 'INSERT INTO userstable(username,password) VALUES (%s,%s);'
    user_list = query_db('SELECT * FROM userstable')['username'].values.tolist()
    if username in user_list:
        st.write('the user already EXISTS')
    else:
        cur.execute(query,(username,password))
        conn.commit()
        st.success("You have successfully created a valid Account")
        st.info("Go to Login Menu to login")


def login_user(username,password):
    query = 'SELECT * FROM userstable WHERE username =%s AND password = %s;'
    cur.execute(query ,(username,password))
    data = cur.fetchall()
    return data
    
import hashlib
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def fields_selectbox():
    sql_field_names = 'select fieldname from fields;'
    field_names = query_db(sql_field_names)['fieldname'].tolist()
    field_name = st.sidebar.selectbox('Choose a field', field_names)
    return field_name
def subjects_selectbox(field_name):
    sql_subject = f"""select S.subjectname
                        from subjects as S, fields as F
                        where S.fieldid = F.fieldid
                        and F.fieldname = '{field_name}';"""
    subject_names = query_db(sql_subject)['subjectname']
    subject_name=st.sidebar.selectbox(f'Select a subject in this field - {field_name}',subject_names)

    return subject_name

def courses_selectbox(subject_name):

    sql_course = f"""select C.coursename
            from courses as C, subjects as S
            where S.subjectid = C.subjectid
            and S.subjectname = '{subject_name}';"""
    course_names = query_db(sql_course)['coursename']
    course_name=st.sidebar.selectbox(f'Select a course in this subject - {subject_name}',course_names)
    
    return course_name

def lessons_selectbox(course_name):
    sql_lesson = f"""select L.lessonname
                    from courses as C, lessons as L
                    where L.courseid = C.courseid
                    and C.coursename = '{course_name}';"""
    lesson_names = query_db(sql_lesson)['lessonname']
    lesson_name=st.sidebar.selectbox(f'select a lesson in this course - {course_name}',lesson_names)
    
    return lesson_name

def video_display(lesson_name):
    sql_video = f"""select V.videolink
                        from videos as V, lessons as L
                        where L.lessonid = V.lessonid
                        and L.lessonname = '{lesson_name}';"""
    if sql_video:     
        videolinks = query_db(sql_video)['videolink']
        if not videolinks.empty:
            f'Displaying the videos in lesson-{lesson_name}'
            video=st.video(videolinks[0])
        else: st.write("We are working on this video.")
def questions_in_lesson(lesson_name):
    if lesson_name:
        sql_questions = f"""select Q.question, Q.Answer
                from lessons as L, questions as Q
                where Q.lessonid = L.lessonid
                and L.lessonname = '{lesson_name}';"""
        questions = query_db(sql_questions)
        if not questions.empty:
            ' ## Questions in this lesson'
            st.write(questions['question'][0])
            if st.button("Answer"):
                st.write(questions['answer'][0]) 
def records(username, lesson_name):
    if username:
        query = '''SELECT * FROM  records as R;'''
        cur.execute(query)
        len_record = cur.fetchall()
        testdf = pd.DataFrame(len_record)
        len_record = len(len_record)
        sql_lessonid = f"""select L.Lessonid
                        from lessons as L
                        where L.lessonname = '{lesson_name}';"""
        lessonid = query_db(sql_lessonid)['lessonid']
        if st.button("Press here to record your progress"):
            ftime = time.strftime("%Y/%m/%d", time.localtime())
            query = 'INSERT INTO records(recordid,username,ftime, lessonid) VALUES (%s,%s,%s,%s);'
            cur.execute(query, (len_record+1,username,ftime,lessonid[0]))
            conn.commit()
            st.write('you have recorded this lesson')
    else:
        st.write('Please log in to record you progress.')
if __name__ == "__main__":
    ### loading things up and initialize
    username = None
    menu = ["Home","Login","SignUp"]
    choice = st.sidebar.radio("Menu",menu)

    # '## Read all tables'
    # sql_all_table_names = "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
    # all_table_names = query_db(sql_all_table_names)['relname'].tolist()
    # table_name = st.selectbox('Choose a table', all_table_names)
    # if table_name:
    #     f'Display the table'

    #     sql_table = f'select * from {table_name};'
    #     df = query_db(sql_table)
    #     st.dataframe(df)
    if choice == "Home":
	    st.subheader("You can go to Menu to login to record the lesson you learned.")
    elif choice == "Login":
        username = st.text_input("User Name")
        password = st.text_input("Password",type='password')
        if st.checkbox("Login"):
            create_usertable()
            hashed_pswd = make_hashes(password)

            result = login_user(username,check_hashes(password,hashed_pswd))
            if result:

                st.success("Logged In as {}".format(username))
                st.subheader("Your records and summary")

                query = '''SELECT R.ftime, count(*)
                            FROM  records as R
                            WHERE Username =%s
                            GROUP BY ftime;'''
                cur.execute(query, (username,))
                record = cur.fetchall()
                dfrecord = pd.DataFrame(record,columns=["date","numbers_of_finshed_lesson_in_this_date"])
                if not dfrecord.empty:
                    # dfrecord.set_index("ftime")
                    st.write(dfrecord)
                    st.markdown('### Your progress in these days')
                    st.line_chart(dfrecord.set_index("date"))
                else: st.write("try to press the button below to record" )
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password",type='password')

        if st.button("Signup"):
            create_usertable()
            add_userdata(new_user,make_hashes(new_password))
            # update_userstable = """select * from userstable;"""
            # df = query_db(update_userstable)
            # df.to_csv('userstableupdata.csv')
            # us = pd.read_csv(os.getcwd()+'/userstableupdata.csv')
            # st.dataframe(us)
            # st.write(os.getcwd())

    select_field = fields_selectbox()
    select_subject = subjects_selectbox(select_field)
    select_course = courses_selectbox(select_subject)
    select_lesson = lessons_selectbox(select_course)
    video_display(select_lesson)
    questions_in_lesson(select_lesson)
    records(username, select_lesson)
