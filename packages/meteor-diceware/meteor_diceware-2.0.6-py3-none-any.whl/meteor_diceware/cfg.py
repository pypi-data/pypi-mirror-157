import os 
import sqlite3 

version = '2.0.6'

SPECIAL_CHARS = r"~!#$%^&*()-=+[]\{}:;,._||" + r'"' + r"'<>?/0123456789"
INSERT_SPECIAL_CHARS = r"0123456789" + r"-_()[]:/.,@#&" 

ProgPath = os.path.dirname(os.path.abspath(__file__))
DBFile = os.path.join(ProgPath , 'db.sqlite')

DB = sqlite3.connect(DBFile)
DBCursor = DB.cursor()

Wordlists = DBCursor.execute("SELECT [name] , total_words from wordlists").fetchall()
Wordlists = {item[0] : item[1] for item in Wordlists}

SELENIUM_DRIVER = None 
SELENIUM_BINARY = None 