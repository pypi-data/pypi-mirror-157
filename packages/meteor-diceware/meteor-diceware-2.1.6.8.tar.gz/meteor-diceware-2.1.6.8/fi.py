import os 
os.environ.update({'METEOR_DICEWARE_INTERNAL_WORDLIST_CREATION_PROCESS_UNDERWAY' : '1'})
from . import utils 

utils.cfg.DBCursor.execute('begin')
utils.cfg.DBCursor.execute('DROP TABLE IF EXISTS wordlists')
utils.cfg.DBCursor.execute('DROP TABLE IF EXISTS main')
utils.cfg.DBCursor.execute('commit')

utils.cfg.DBCursor.executescript(open(os.path.join(utils.cfg.ProgPath , 'init.sql') , 'r' , encoding = 'utf8').read())
dwaretxt = os.path.join(utils.cfg.ProgPath, 'actual_diceware.txt')

words = utils.clean(open(dwaretxt , 'r' , encoding = 'utf8').read())
utils.create('main' , words = words ,  description = 'Original Diceware Wordlist')
utils.recount('main')

try:
    
    utils.cfg.DB.commit()
    
except:
    
    pass 