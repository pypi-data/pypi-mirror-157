from . import utils 


utils.create('main' , file = dwaretxt ,  description = 'Original Diceware Wordlist')

try:
    utils.cfg.DB.commit()
    
except:
    pass 