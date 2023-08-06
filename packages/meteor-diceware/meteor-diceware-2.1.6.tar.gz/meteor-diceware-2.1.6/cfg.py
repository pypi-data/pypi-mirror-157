import os 
import sqlite3 

__version__ = version = '2.1.6'

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
        
    os.environ.update({'METEOR_DICEWARE_INTERNAL_WORDLIST_CREATION_PROCESS_UNDERWAY' :  '1' })   
    subprocess.call([sys.executable, '-m' , 'meteor_diceware.utils' , 'create' , 'main' , '-w'] , env = os.environ)
    subprocess.call([sys.executable , '-m' , 'meteor_diceware.utils' , 'edit' , 'main' , '-f' , os.path.join(ProgPath , 'actual_diceware.txt')] , env = os.environ )

__initdb = lambda : DBCursor.executescript(open(os.path.join(ProgPath , 'init.sql') , 'r' , encoding = 'utf8').read())


try:
    
    __selroutine()
    
    if len(Wordlists) == 0 :
        __sroutine1()
    
    __selroutine()
    
except sqlite3.OperationalError:
    
    __initdb()
    
    if 'METEOR_DICEWARE_INTERNAL_WORDLIST_CREATION_PROCESS_UNDERWAY' in os.environ:
        Wordlists = {}
    
    else:        
        __sroutine1()
        __selroutine()
    
except:
    
    raise 

