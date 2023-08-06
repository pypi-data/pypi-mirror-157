import os 
from functools import lru_cache 


@lru_cache(maxsize = 4)
def get_log(n , base = 8):
    
    import math 
    return math.ceil(math.log(n, base)) 

def base0caller( length : int = 7776 , keypush : int = 3 , offset_meter  : int = 4 ):		##7776 is the default length of diceware 

	offset_meter = ((keypush + 1)>>2) + 2  
	baserem = (1<<keypush) - 1 
	counter = 0 
	rounds = get_log(length , 1<<keypush)
 
	for i in range(rounds):

		counter1 = int.from_bytes(os.urandom(offset_meter) , 'big' ) 
		counter = (counter << keypush) | (counter1&baserem)
		offset_meter = (counter1 & 0xf)

	return counter % length 

DiceCalls = lambda  min_ = 0 , max_ = 7776: base0caller(max_ - min_) + min_ 
