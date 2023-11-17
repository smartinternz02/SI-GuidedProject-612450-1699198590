import sqlite3

conn = sqlite3.connect('Calorie.db')
cur = conn.cursor()
cur.execute('''create table if not exists users (
            userid text primary key, 
            password text, 
            name text,
            age text,
            height text,
            gender text)''')

cur.execute('''create table if not exists exercise (
            exercise_id text primary key,
            exercise_name text,
            userid text,
            duration text,
            date text,
            bpm text,
            temperature text,
            calories text)''')

conn.commit()
conn.close()