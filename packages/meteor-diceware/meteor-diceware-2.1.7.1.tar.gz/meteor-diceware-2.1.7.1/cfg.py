import os, sys  
import sqlite3 

__version__ = version = '2.1.7.1'

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
 
if 'METEOR_DICEWARE_INTERNAL_WORDLIST_CREATION_PROCESS_UNDERWAY' in os.environ:
    print("Underprocess")
    Wordlists = {}
    
else:

    
    try:
        
        __selroutine()
        
        if len(Wordlists) == 0  :
            raise PermissionError(f"Wordlists have not been generated yet. Please use :: `{sys.executable} -m diceware.fi`")
            
    except sqlite3.OperationalError:
        
        raise PermissionError(f"Wordlists have not been generated yet. Please use :: `{sys.executable} -m diceware.fi`")
            
    except:
        
        raise 

