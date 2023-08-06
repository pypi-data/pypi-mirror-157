import os, sys  
import sqlite3 

__version__ = version = '2.2.1'

SPECIAL_CHARS = r"~!#$%^&*()-=+[]\{}:;,._||" + r'"' + r"'<>?/0123456789"
INSERT_SPECIAL_CHARS = r"0123456789" + r"-_()[]:/.,@#&" 

ProgPath = os.path.dirname(os.path.abspath(__file__))
DBFile = os.path.join(ProgPath , 'db.sqlite3')

DB = sqlite3.connect(DBFile)
DBCursor = DB.cursor()


SELENIUM_DRIVER = None 
SELENIUM_BINARY = None 

"""
First Installation Configuration Process 
And `Wordlists` are created below 
"""

def __selroutine():

    global DBCursor, Wordlists 
        
    Wordlists = DBCursor.execute("SELECT [name] , total_words from wordlists").fetchall()
    Wordlists = {item[0] : item[1] for item in Wordlists}

def __insert_routine1(wlist_copy : bool = True , main_copy  : bool = True): 
    
    global DBCursor, ProgPath 
    
    if (wlist_copy == False) and (main_copy == False):
        return None 
    
    copydb = os.path.join(ProgPath , 'default.sqlite3')
    
    DBCursor.execute('begin')
    DBCursor.execute(f'ATTACH DATABASE "{copydb}" as default_database')
    
    if main_copy:
        DBCursor.execute('CREATE TABLE main as select * from default_database.main')
        
    if wlist_copy:
        DBCursor.execute('CREATE TABLE wordlists as select * from default_database.wordlists')
        
    
    if (wlist_copy == False) and (main_copy == True):
        DBCursor.execute('INSERT INTO wordlists SELECT * from default_database.wordlists WHERE name = "main"') 
    
    DBCursor.execute("commit")        
    DBCursor.execute('DETACH DATABASE default_database')
        
    return None 

try:
    
    __selroutine()
    
    if len(Wordlists) == 0  :
        __insert_routine1(False , True)
        __selroutine()
    
except sqlite3.OperationalError:
    
    __insert_routine1(True , True)
    __selroutine() 
    
except:
    
    raise 

