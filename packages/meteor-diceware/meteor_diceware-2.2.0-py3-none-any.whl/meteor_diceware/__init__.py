from argparse import ArgumentParser, Namespace 
from .  import  cfg 
import sys, os  
from random import SystemRandom

systemrandom = SystemRandom() 

def arguments(args : list = None):
    
	parser = ArgumentParser(description = 'Create a passphrase' , prog = 'Meteor-Diceware' , epilog = f'Wordlists are stored in {cfg.DBFile}\
		Use meteor_diceware.utils for generating/freezing/editing/concatenating password lists' )

	parser.add_argument('-v' , '--version' , action = 'version' , version = f'{cfg.version}' , help = 'Prints the version of the program')
 
	parser.add_argument('-n' , '--num' , 
						dest = 'count' , action = 'store' , type = int, default = 6 , 
						help = 'number of words to concatenate. Default: 6')

	parser.add_argument('--no-caps' , action = 'store_false' , dest = 'caps', help = 'Turn off capitalization.')

	parser.add_argument('-w' , '--wordlist' , 
						dest = 'wordlist' , action = 'store' , choices = cfg.Wordlists.keys() , metavar = '..' , default = 'main' , 
						help = f'Wordlist to choose words from. Possible Choices: {set(cfg.Wordlists.keys())}. Defaults to main' )

	parser.add_argument('-d' , '--delimiter' , '--delim' , 
						dest = 'delimiter' , action = 'store' , default = '_' , 
						help = 'Delimiter to set between words. Defaults to _')

	parser.add_argument('-s' , '--special' , '--specials' , 
						dest = 'specials' , action = 'store' , type = int , default = 0 , metavar = 'n' , 
						help =  'Insert n special chars into generated word')

	if args == None: 

		return parser.parse_args()


	return parser.parse_args(args )

def FiltrationArguments(options : Namespace):

	return options 

def insert_special_char(word, specials= cfg.SPECIAL_CHARS):
	
	pos = DiceCalls()%len(word)
	char = DiceCalls()%len(specials)
	
	return word[:pos] + specials[char] + word[pos:]


##NOTE:: The old DiceCalls code is stored in dicecalls.proc.py   

DiceCalls = lambda min_ = 0 , max_ = 7776 : systemrandom.randint(min_, max_)

def get_word(wordlist , counter ):
	
	return cfg.DBCursor.execute(f'SELECT word from {wordlist} WHERE counter = ?' , (counter, )).fetchone()[0]
	
def machinery(n , d, s , w : str = None , caps : bool = False):

	global rnd 

	if w is None:
     
		w = rnd.choice(cfg.Wordlists.keys())
		

	if n == 0 :
		raise ValueError(f'At least need to generate one word')

	if caps:
		normalize = lambda x : x.lower().capitalize()

	else:
		normalize = lambda x : x.lower()

	if not w in cfg.Wordlists:
		raise ValueError(f'Wordlist `{w}` does not exist')
	
	max_len = cfg.Wordlists[w]	
 
	words = [get_word(w , DiceCalls(0, max_len)) for _ in range(n)]
	words = [normalize(word) for word in words]
 
	word = d.join(words) 
	del words
	
	for _ in range((s) ):
		word = insert_special_char(word)
	
	
	return word 
 
def DriverMain(options : Namespace):
    
    return machinery(options.count , options.delimiter , options.specials , options.wordlist , options.caps )

if __name__ ==  "__main__": 
	
	sys.stdout.write(DriverMain(FiltrationArguments(arguments())))

	