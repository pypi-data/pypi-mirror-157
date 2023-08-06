import logging 
import sqlite3 

logger = logging.getLogger('diceware-snowflake')
clean = None 

def edit_meta(DBCursor : sqlite3.Cursor , wordlist : str):
    
    DBCursor.execute('begin')
    DBCursor.execute(f"UPDATE wordlists SET total_words = (SELECT COUNT(*) FROM {wordlist}), updated_at = CURRENT_TIMESTAMP WHERE name = ?" , (wordlist , ))
    DBCursor.execute('commit')
    return True

def produce_edit_stats(stats : dict):
    
    import termcolor, colorama 
    colorama.init(autoreset=True)
    
    if stats['mode'] == 'remove':
        
        j = stats['input'] + stats['final'] - stats['init'] 
        
        print(termcolor.colored('Initial Number of Words:: ' , 'yellow') , termcolor.colored(stats['init'] , 'green') , '\n' , 
              termcolor.colored('Final Number of Words:: ' , 'yellow') , termcolor.colored(stats['final'] , 'green') , '\n' ,
              termcolor.colored('Total Words Inputted::' , 'yellow') , termcolor.colored(stats['input'] , 'green' ) , '\n' , 
              termcolor.colored('Total Successful Deletes:: ' , 'yellow') , termcolor.colored(stats['init'] - stats['final'] , 'green' )  , '\n' , 
              termcolor.colored('Total Repeats:: ' , 'yellow'  ) , termcolor.colored(j , 'red' if j > 0 else 'green' ) , 
              sep = '' , end = '\n' 
        ) 
    
    elif stats['mode'] == 'add':
        
        j = stats['input'] - stats['final'] + stats['init'] 
        
        print(termcolor.colored('Initial Number of Words:: ' , 'yellow') , termcolor.colored(stats['init'] , 'green') , '\n' , 
              termcolor.colored('Final Number of Words:: ' , 'yellow') , termcolor.colored(stats['final'] , 'green') , '\n' ,
              termcolor.colored('Total Words Inputted::' , 'yellow') , termcolor.colored(stats['input'] , 'green' ) , '\n' , 
              termcolor.colored('Total Successful Inserts:: ' , 'yellow') , termcolor.colored(-stats['init'] + stats['final'] , 'green' )  , '\n' , 
              termcolor.colored('Total Repeats:: ' , 'yellow'  ) , termcolor.colored(j , 'red' if j > 0 else 'green' ) , 
              sep = '' , end = '\n' 
        )
        
    elif stats['mode'] == 'range':

        termcolor.cprint('Total Number of Words in Wordlist Presently::' , 'yellow' , end = '')
        termcolor.cprint(stats['final'] , 'green')
        
    colorama.deinit()

def check_wordlist(wordlist : str , DBCursor : sqlite3.Cursor):
    
    if not  bool(DBCursor.execute('SELECT COUNT(*) FROM wordlists where name = ?' , (wordlist,)).fetchone()[0] == 1 ):
        raise KeyError(f'Wordlist `{wordlist}` does not exist in the database')

def add(DBCursor : sqlite3.Cursor , wordlist : str , file : str , words : list): 

    stats = {   'mode' : 'add' , 
                'init' :  DBCursor.execute(f"SELECT COUNT(*) FROM {wordlist}").fetchone()[0]
    }
    
    i = 0 
    
    
    if (file is None) and (words is None):
        raise ValueError(f'Both file and words cannot be None for editing')

    DBCursor.execute("begin")

    if file is not None:
        
        with open(file , 'r' , encoding = 'utf8') as handle:
            for line in handle:
                line_words = clean(line)            ##Dont use this as words since it is a parameter 
                i += len(line_words)
                DBCursor.executemany(f"INSERT INTO {wordlist} (word) VALUES (?)" , [[word] for word in line_words])    
                
                
    if words is not None:
        DBCursor.executemany(f'INSERT INTO {wordlist} (word) VALUES (?)' , [[word] for word in words])
        i += len(words)
    
    DBCursor.execute("commit")
    
    logger.info(f'Successfully Injected {i} words')        
    logger.info(f'Successfully Edited {wordlist}')
    
    stats['final'] = DBCursor.execute(f"SELECT COUNT(*) FROM {wordlist}").fetchone()[0]
    stats['input'] = i 

    return stats 

def remove(DBCursor : sqlite3.Cursor , wordlist : str , file : str , words : list):
    
    stats = {   'mode' : 'add' , 
                'init' :  DBCursor.execute(f"SELECT COUNT(*) FROM {wordlist}").fetchone()[0]
    }
    
    i = 0 
    
    
    if (file is None) and (words is None):
        raise ValueError(f'Both file and words cannot be None for editing')

    DBCursor.execute('begin')
    DBCursor.execute(f'CREATE TABLE {wordlist}_temp(word TEXT PRIMARY KEY ON CONFLICT IGNORE);')
    
    if file is not None:
        
        with open(file , 'r' , encoding = 'utf8') as handle:
            for line in handle:
                line_words = clean(line)            ##Dont use this as words since it is a parameter 
                i += len(line_words)
                DBCursor.executemany(f"INSERT INTO {wordlist}_temp (word) VALUES (?)" , [[word] for word in line_words])    
                
                
    if words is not None:
        DBCursor.executemany(f'INSERT INTO {wordlist}_temp (word) VALUES (?)' , [[word] for word in words])
        i += len(words)
    
    DBCursor.execute(f'ALTER TABLE {wordlist} RENAME TO temp_{wordlist}')
    DBCursor.execute(f'CREATE TABLE {wordlist} AS (SELECT word from temp_{wordlist} WHERE word NOT IN (SELECT word from {wordlist}_temp ) );')
    DBCursor.execute(f'DROP TABLE temp_{wordlist}')
    DBCursor.execute(f'DROP TABLE {wordlist}_temp')
    
    DBCursor.execute('commit')
    
    logger.info(f'Successfully Injected {i} words')        
    logger.info(f'Successfully Edited {wordlist}')
    
    stats['final'] = DBCursor.execute(f"SELECT COUNT(*) FROM {wordlist}").fetchone()[0]
    stats['input'] = i 

    return stats 
    
def ranger(DBCursor : sqlite3.Cursor , wordlist : str  ,  range_start : int = None , range_end : int = None ):
    
    DBCursor.execute('begin')
    
    logger.info(f'Selecting RANGE:: {range_start}:{range_end}')
    DBCursor.execute(f'ALTER TABLE {wordlist} RENAME TO {wordlist}_temp')

    DBCursor.execute(f'CREATE TABLE {wordlist} AS SELECT word FROM {wordlist}_temp ORDER BY len(word) ASC LIMIT {range_end - range_start} OFFSET {range_start}')    
    DBCursor.execute(f'DROP TABLE {wordlist}_temp')
    
    
    logger.info('Successfully trimmed table')
    DBCursor.execute("commit")
    
    return {'mode' : 'ranger' , 'final' : DBCursor.execute(f"SELECT COUNT(*) FROM {wordlist}").fetchone()[0]}

def len_filter(DBCursor : sqlite3.Cursor , wordlist : str  , len_min : int = None , len_max : int =  None):
    
    init = DBCursor.execute(f'SELECT COUNT(*) FROM {wordlist}').fetchone()[0]
    
    
    if (len_max is None) and (len_min is None):
        
        logger.info(f'Pre-Filter:: No filter needed')
        return None 
    
    if len_max == None:
        
        logger.info(f'Len-Filter::Min={len_min}')    
        DBCursor.execute('begin')
        DBCursor.execute(f'DELETE FROM {wordlist} WHERE length(word) < ?' , (len_min , ))
        DBCursor.execute('commit')
        
    elif len_max == None:
        
        
        logger.info(f'Len-Filter::Max={len_max}')
        DBCursor.execute('begin')
        DBCursor.execute(f'DELETE FROM {wordlist} WHERE length(word) > ?' , (len_max , ))
        DBCursor.execute('commit')
        
    else:
        
        
        logger.info(f'Len-Filter::(Min,Max)=({len_min},{len_max})')
        DBCursor.execute('begin')
        DBCursor.execute(f'DELETE FROM {wordlist} WHERE length(word) NOT BETWEEN ? AND ?' , (len_min , len_max))
        DBCursor.execute('commit')