import os 
import sqlite3 

__version__ = version = '2.1.6.6'

SPECIAL_CHARS = r"~!#$%^&*()-=+[]\{}:;,._||" + r'"' + r"'<>?/0123456789"
INSERT_SPECIAL_CHARS = r"0123456789" + r"-_()[]:/.,@#&" 

ProgPath = os.path.dirname(os.path.abspath(__file__))
DBFile = os.path.join(ProgPath , 'db.sqlite')

DB = sqlite3.connect(DBFile)
DBCursor = DB.cursor()


SELENIUM_DRIVER = None 
SELENIUM_BINARY = None 

def __selroutine():

    global DBCursor, Wordlists 
        
    Wordlists = DBCursor.execute("SELECT [name] , total_words from wordlists").fetchall()
    Wordlists = {item[0] : item[1] for item in Wordlists}
 
def __sroutine1():
    
       
    global ProgPath, DB, DBCursor, DBFile  
    os.environ.update({'METEOR_DICEWARE_INTERNAL_WORDLIST_CREATION_PROCESS_UNDERWAY' :  '1' })   
    DB.close()
    
    import runpy 
    runpy.run_path(os.path.join(ProgPath , 'failsafe.py') , init_globals  = {'dwaretxt' : os.path.join(ProgPath , 'actual_diceware.txt')})
    
    DB = sqlite3.connect(DBFile)
    DBCursor = DB.cursor()
    
    return None     
    
__initdb = lambda : DBCursor.executescript(open(os.path.join(ProgPath , 'init.sql') , 'r' , encoding = 'utf8').read())

if 'METEOR_DICEWARE_INTERNAL_WORDLIST_CREATION_PROCESS_UNDERWAY' in os.environ:
    Wordlists = {}
    
else:

    try:
        
        __selroutine()
        
        if len(Wordlists) == 0  :
            __sroutine1()
        
        __selroutine()
        
    except sqlite3.OperationalError:
        
        __initdb()        
        __sroutine1()
        __selroutine()
        
    except:
        
        raise 

