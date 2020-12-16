import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser
 
'# Demo: Streamlit + Postgres'
 
@st.cache
def get_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}
 
 
@st.cache
def query_db(sql: str):
    # print(f'Running query_db(): {sql}')
 
    db_info = get_config()
 
    # Connect to an existing database
    conn = psycopg2.connect(**db_info)
 
    # Open a cursor to perform database operations
    cur = conn.cursor()
 
    # Execute a command: this creates a new table
    cur.execute(sql)
 
    # Obtain data
    data = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
 
    # Make the changes to the database persistent
    conn.commit()
 
    # Close communication with the database
    cur.close()
    conn.close()
 
    df = pd.DataFrame(data=data, columns=column_names)
 
    return df
 
 
'## Read tables'
 
sql_all_table_names = "select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"
all_table_names = query_db(sql_all_table_names)['relname'].tolist()
table_name = st.selectbox('Choose a table', all_table_names)
if table_name:
    f'Display the table'
 
    sql_table = f'select * from {table_name};'
    df = query_db(sql_table)
    st.dataframe(df)
'## Query customers'
 
sql_customer_names = 'select name from customers;'
customer_names = query_db(sql_customer_names)['name'].tolist()
customer_name = st.selectbox('choose a customer', customer_names)
if customer_name:
    sql_customer = f"select * from customers where name = '{customer_name}';"
    customer_info = query_db(sql_customer).loc[0]
    c_age, c_city, c_state = customer_info['age'], customer_info['city'], customer_info['state']
    st.write(f"{customer_name} is {c_age}-year old, and lives in {customer_info['city']}, {customer_info['state']}.")
'## Query orders'
 
sql_order_ids = 'select order_id from orders;'
order_ids = query_db(sql_order_ids)['order_id'].tolist()
order_id = st.radio('choose a customer', order_ids)
if order_id:
    sql_order = f"""select C.name, O.order_date
                    from orders as O, customers as C 
                    where O.order_id = {order_id}
                    and O.customer_id = C.id;"""
    customer_info = query_db(sql_order).loc[0]
    customer_name = customer_info['name']
    order_date = customer_info['order_date']
    st.write(f'This order is placed by {customer_name} on {order_date}.')
'## Query field'

sql_field_names = 'select fieldname from field;'
field_names = query_db(sql_field_names)['fieldname'].tolist()
field_name = st.selectbox('choose a field', field_names)
if field_name:
    f'Display the subjects in this field'
    sql_subject = f"""select S.subjectname
                    from subject_contain as S, field as F
                    where S.fieldid = F.fieldid
                    and F.fieldname = '{field_name}';"""
    df = query_db(sql_subject)['subjectname']
    st.write(f'This order is placed by {field_name}')
    st.radio(f'select a subject in this field {field_name}',df)

'## display video'

sql_video_names = 'select videoname from video;'
video_names = query_db(sql_video_names)['videoname'].tolist()
video_name = st.selectbox('choose a video', video_names)
if video_name:
    f'Display the video'
    sql_video = f"""select V.videolink
                    from video as V
                    where V.videoname ='{video_name}'"""
    sql_video

'## Radio: List all the customers live in the selected city'
sql_cities = 'select distinct city from customers;'
cities = query_db(sql_cities)['city'].tolist()
city_radio = st.radio('Choose a city', cities)
if city_radio:
    sql_customers = f"select name from customers where city = '{city_radio}' order by name;"
    customer_names = query_db(sql_customers)['name']
    st.dataframe(customer_names)
 
'## Multiselect: List all the customers live in the selected cities'
sql_cities = 'select distinct city from customers;'
cities = query_db(sql_cities)['city'].tolist()
city_mulsel = st.multiselect('Choose a city', cities)
if city_mulsel:
    city_mulsel_str = ','.join(["'" + city + "'" for city in city_mulsel]) 
    # select city, name from customers where city in ('Waterloo','') order by city, name;
    sql_customers = f"select city, name from customers where city in ({city_mulsel_str}) order by city, name;"
    city_customer = query_db(sql_customers)
    st.dataframe(city_customer)
