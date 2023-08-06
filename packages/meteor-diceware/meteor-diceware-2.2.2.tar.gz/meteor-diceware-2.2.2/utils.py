from argparse import ArgumentParser, Namespace 
import logging 
import sqlite3 
import os
import sys 

from . import cfg
import re

WORDPATTERN = re.compile( r"\b\w*[A-Z|a-z]\w*\b" ,re.IGNORECASE|re.ASCII|re.MULTILINE )    ##Original Diceware prevents non-unicode words from being used in the wordlist  

GENERATE_ALIASES = ('generate', 'gen' , 'make' , 'create')
EDIT_ALIASES = ('edit' , 'modify' , 'change')
SHOW_ALIASES = ('show' , 'info' , 'view' , 'stats')
FREEZE_ALIASES = ('freeze' , 'freeze-list' , 'store' , 'print' , 'freeze-content')
DELETE_ALIASES = ('rm' , 'remove' , 'delete' , 'del')
LIST_ALIASES = ('list' , 'ls' , 'list-all' , 'lsd')
COPY_ALIASES = ('copy' , 'cp')
CONCAT_ALIASES = ('cat' , 'concat' , 'join' , 'union')
RECOUNT_ALIASES = ('recount' , 'index' , 'reindex' , 'counter-set' , 'index-rebuild')
BACKUP_ALIASES = ('backup' , 'create-copy')
RESTORE_ALIASES = ('restore' , 'reinstate' , 'restore-wordlist')
HISTOGRAM_ALIASES = ('hist' , 'histogram' , 'statgram')
SCRAPER_ALIASES = ('scraper' , 'scrape' , 'scrape-page')
SNOWFLAKE_ALIASES = ('explain' , 'snowflake' , 'snowflake-explain')

DBCursor = cfg.DBCursor 
 

if __name__ == '__main__':
    logger = logging.getLogger('diceware-utils')  
else:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

def arguments(args : list = None):

    parser = ArgumentParser(prog = "Diceware.utils" , description = "Helper Utilities for Meteor-Diceware" , epilog = "Use meteor_diceware.__init__ for diceware generated passwords" , allow_abbrev = True) 
    p = parser.add_subparsers(title = 'Actions' , description = "Different Actions to choose from" , dest = 'action')
    
    generate = p.add_parser(GENERATE_ALIASES[0] , help = 'Generate a new wordlist' , aliases = GENERATE_ALIASES[1:])
    edit = p.add_parser(EDIT_ALIASES[0] , help = 'Edit an existing wordlist'  , aliases = EDIT_ALIASES[1:] )  
    show = p.add_parser(SHOW_ALIASES[0] , help = "Show important information about a wordlist" , aliases = SHOW_ALIASES[1:])
    freeze = p.add_parser(FREEZE_ALIASES[0] , help = "Freeze a wordlist" , aliases = FREEZE_ALIASES[1:])
    remove = p.add_parser(DELETE_ALIASES[0], help = "Remove a wordlist" , aliases = DELETE_ALIASES[1:])
    _list = p.add_parser(LIST_ALIASES[0] , help = 'Lists all the wordlists with important statistics' , aliases = LIST_ALIASES[1:])
    copy = p.add_parser(COPY_ALIASES[0] , help = 'Create a copy of a wordlist' , aliases = COPY_ALIASES[1:])
    concat = p.add_parser(CONCAT_ALIASES[0] , help = 'Concatenate one or more wordlists into another' , aliases = CONCAT_ALIASES[1:])
    recount = p.add_parser(RECOUNT_ALIASES[0] , help = 'Initialize Counters on a Wordlist once again' , aliases = RECOUNT_ALIASES[1:])        
    backup = p.add_parser(BACKUP_ALIASES[0] , help = 'Backup the database to another file' , aliases = BACKUP_ALIASES[1:])    
    restore = p.add_parser(RESTORE_ALIASES[0] , help = 'Restore the database from a backup file' , aliases = RESTORE_ALIASES[1:])
    histogram = p.add_parser(HISTOGRAM_ALIASES[0] , help = 'Make a histogram of a wordlist' , aliases = HISTOGRAM_ALIASES[1:])
    scraper = p.add_parser(SCRAPER_ALIASES[0] , help = 'Scrape a webpage for words' , aliases = SCRAPER_ALIASES[1:])
    explain_snowflake = p.add_parser(SNOWFLAKE_ALIASES[0] , help = 'Explains the Snowflake flag' , aliases = SNOWFLAKE_ALIASES[1:])
    
    for _parser in (edit ,  freeze , copy , histogram , scraper):
        _parser.add_argument(dest = 'wordlist' , choices = cfg.Wordlists,  help = 'The wordlist to use' )
    
    generate.add_argument( dest = 'wordlist',  help = f'The wordlist to generate. Note that these already exist:: {cfg.Wordlists}')
    
    for _parser in (remove , show , concat , recount, backup ):
        _parser.add_argument(dest = 'wordlist', nargs = '+' , choices = cfg.Wordlists , help = 'The list of wordlists')
    
    for _parser in (copy , concat):
        
        _parser.add_argument('-t' , '--target' , dest = 'target', required = True , help = 'The target wordlist for the operation')
    
    freeze.add_argument(    '-f' , '--file' , '-o' , '--output' , dest = 'output' , default = None ,  type = os.path.abspath  , 
                            help = 'File to freeze output to. By default prints to terminal if no file given')
    
    scraper.add_argument('--links' , dest = 'links' , nargs = '+' , help = 'The links to scrape' )
    scraper.add_argument('--responsive' , '--scroll' , dest = 'responsive' , action = 'store_true' , help = 'For responsive webpages that need to be scrolled down')
    
    backup.add_argument(    '-o' , '--output' , dest = 'output' , default = None , type = os.path.abspath , help = 'Output file to backup to')
    
    
    h1 = histogram.add_mutually_exclusive_group()
    h1.add_argument('-o' , '--output' , dest = 'output' , default = None , type = os.path.abspath , help = 'Output csv file to create histogram at')
    h1.add_argument('-g' , '--graphic' , dest = 'graphic' , action = 'store_true' , help = 'Create a histogram graphic')
    h1.add_argument('-t' , '--tabular' , dest = 'tabular' , action = 'store_true' , help = 'Create a tabular histogram')
       
    
    restore.add_argument(dest = 'file' , type = os.path.abspath , help = 'The file to restore from')
    restore.add_argument('-w' , '-W' , dest = 'wordlists' , nargs = '+' , default = None , help = 'The list of wordlists to restore')
    
    edit.add_argument('--edit-flag' ,  '--snowflake' , '--snowflake-flag' , dest = 'snowflake' , default = '+' , 
    help = f'Different Edit options as defined in Snowflake Flag Manual @{os.path.join(cfg.ProgPath , "snowflake.pdf")}')
    
    for _parser in (generate , edit):
        
        _parser.add_argument('-f' , '--file' , '-o' , '--output' , dest = 'file' , default = None , type = os.path.abspath  ,
                             help = "File to use for words")
        
        _parser.add_argument('-w' , '-W' ,  '--words' , nargs = '*' , dest = 'words' , default = None , help = 'Use words directly instead of providing a file' )

    for _parser in (generate, edit , concat):
    
        _parser.add_argument('-d' , '--description' , default = None , help = 'Description of the wordlist')
        
    if args is None:
        return parser.parse_args()
    
    return parser.parse_args(args)
    
def show(wordlist):
    
    import colorama, termcolor 
    colorama.init(autoreset = True)
    
    pk , total_words, created_at , updated_at , description = \
        cfg.DBCursor.execute('SELECT pk , total_words, created_at , updated_at , description  FROM wordlists WHERE name = ?' , (wordlist , )).fetchone() 
    logger.info(f'Obtained information on {wordlist}')

    cfg.DB.create_function('len' , 1 , len)
    longest = cfg.DBCursor.execute(f'SELECT word from {wordlist} ORDER BY len(word) DESC LIMIT 1').fetchone()[0]
    shortest = cfg.DBCursor.execute(f'SELECT word from {wordlist} ORDER BY len(word) ASC LIMIT 1').fetchone() [0]
    logger.info(f'Obtained longest and shortest words from {wordlist}')
    
    vals = {'Wordlist Name' : wordlist , 
            'Created At' : created_at  ,
            'Last Updated At' : updated_at , 
            'Description' : description , 
            'Total Number of Words' : total_words , 
            'Longest Word' : f'{len(longest)} :: {longest}' ,
            'Shortest Word' : f'{len(shortest)} :: {shortest}' }
    
    lmax = len(max(vals , key = len))
    
    print('\n\n' , end = '')
    for key , value in vals.items():
        
        termcolor.cprint(key.ljust(lmax) , end = '' , color = 'yellow')
        print(' : ' , end = '' )
        termcolor.cprint(value , end = '\n' , color = 'green')
        
    colorama.deinit()

clean = lambda line : WORDPATTERN.findall(line.lower() ) 
   
def recount(wordlist ):
    
    DBCursor.execute('begin')
    Cursor2 = cfg.DB.cursor()

    try:    
        
        try:
            DBCursor.execute(f'ALTER TABLE {wordlist} DROP COLUMN counter;')
        
        except sqlite3.Error:
            logger.info(f"Recount::Counter did not exist on {wordlist}")
            
        DBCursor.execute(f"ALTER TABLE {wordlist} ADD counter INTEGER;")
        
        counter = -1 
        def ticker(word):
            
            nonlocal counter 
            
            counter +=1 
            return counter 
         
        cfg.DB.create_function('ticker' , 1 , ticker) 
        DBCursor.execute(f'UPDATE {wordlist} SET counter = ticker(word);')
        DBCursor.execute('commit')

    except:
        
        logger.error("Recount Failed; Re-execute recount operation")
        DBCursor.execute('rollback')
        raise 
    
    logger.info(f'Recount successfully completed')
    count = DBCursor.execute(f'SELECT COUNT(counter) FROM {wordlist}').fetchone()[0]
    logger.info(f'TOTAL WORDS in {wordlist}::{count}')
    
    
    
    DBCursor.executescript(f'begin;UPDATE wordlists SET total_words = {count}, updated_at = CURRENT_TIMESTAMP WHERE name = "{wordlist}";commit;')
    return count 
    
def create(wordlist , file , words , description : str = None ) :
    
    
    if wordlist in ( 'wordlists' , 'sqlite_master' , 'sqlite_sequence' , 'sqlite_schema') :
        raise PermissionError(f'`{wordlist}` is an internal table and thus cannot be used as the name for a regular wordlist' )
    
    elif wordlist in cfg.Wordlists:
        raise ValueError(f'Wordlist `{wordlist}` already exists. Consider editing')
    
    elif wordlist.lower().startswith('temp') or wordlist.lower().endswith('temp'):
        
        raise PermissionError(f'Wordlist name cannot start or end with temp due to operational restrictions')
    
    elif not re.match('^[\w|\_]+$' , wordlist):
        
        raise ValueError(f'The wordlist can only contain of letters A-Z/a-z, numbers, and underscores')
    
    if (file is None) and (words is None):
        raise ValueError(f'Both file and words cannot be None for creation')
    
    if description is None:
        description = 'Standard Wordlist'
        logger.info(f'No description given for wordlist. Tend to give descriptions for better understanding')
        
    try:
        cfg.DBCursor.execute("begin")
        cfg.DBCursor.execute(f'CREATE TABLE {wordlist}(word TEXT PRIMARY KEY ON CONFLICT IGNORE);')
        cfg.DBCursor.execute('INSERT INTO wordlists (name , description) VALUES (?,?)' , (wordlist , description))
        
        
        if file is not None:
            
            with open(file , 'r' , encoding = 'utf8') as handle:
                for line in handle:
                    line_words = clean(line.strip())            ##Dont use this as words since it is a parameter 
                    cfg.DBCursor.executemany(f"INSERT INTO {wordlist} (word) VALUES (?)" , [[word] for word in line_words])    
                    
                    
        if words is not None:
        
            if len(words) == 0 :
                
                logger.warning(f'Since -w was passed but no words were provided, it is assumed that the purpose is to create a wordlist without any words')

            else:
                cfg.DBCursor.executemany(f'INSERT INTO {wordlist} (word) VALUES (?)' , [[word] for word in words])
        
            
        count = cfg.DBCursor.execute(f'SELECT COUNT(*) FROM {wordlist}').fetchone()[0]
        cfg.DBCursor.execute('''UPDATE 
                                    wordlists 
                                SET 
                                    total_words = ?, 
                                    created_at = CURRENT_TIMESTAMP , 
                                    updated_at = CURRENT_TIMESTAMP 
                                WHERE 
                                    name = ?''' , 
                            (count  , wordlist))
        
        
        cfg.DBCursor.execute('commit')
    
    except sqlite3.Error as e: 
        
        logger.critical('Cancelling CREATE operation')
        cfg.DBCursor.execute('rollback')
        logger.critical(f'INFO ON ERROR:: {e}')
    
    except:
        
        cfg.DBCursor.execute('rollback')
        raise 
    
    
    logger.info(f'Wordlist `{wordlist}` and corresponding statistics successfully pushed to the database')
    #recount(wordlist)
    return None 

def edit(wordlist , file , words , snowflake = '+' , description : str = None):
    
    snowflake = snowflake.strip().lower()
    
    if description is not None:
        cfg.DBCursor.execute("begin")
        cfg.DBCursor.execute("UPDATE wordlists SET description = ? WHERE name = ?" , (description , wordlist))
        cfg.DBCursor.execute("commit")
        
    if wordlist not in cfg.Wordlists:
        raise ValueError(f"Wordlist {wordlist} does not exist in the database")
    
    from . import snowflake as snowflake_driver
    snowflake_driver.clean = clean ##This is a hack to make sure the snowflake driver uses the same clean function
    
    if snowflake == '':
        
        logger.info('Exiting on blank snowflake flag')
        return None 
    
    if snowflake == '+':

        stats = snowflake_driver.add(cfg.DBCursor , wordlist , file  , words)
        snowflake_driver.edit_meta(DBCursor , wordlist) 
        snowflake_driver.produce_edit_stats(stats)
        #recount(wordlist)
        
        return True        
        
    elif snowflake == '-':
        
        stats = snowflake_driver.remove(cfg.DBCursor, wordlist , file , words)
        snowflake_driver.edit_meta(DBCursor , wordlist) 
        snowflake_driver.produce_edit_stats(stats)
        #recount(wordlist)
        
        
    elif re.match(r'^\-?\d*\:\-?\d*$' , snowflake):
        
        range_ = [ item for item in snowflake.split(':') if len(item) > 0 ]
        count = cfg.Wordlists[wordlist]
        
        if len(range_) == 1:
            
            if snowflake.startswith('-:') or snowflake.startswith(':'):
                range_start = 0
                range_end = int(range_[0])
                
            else:
                
                range_start = int(range_[0])
                range_end = count 
            
        else:
            range_ = [int(x) for x in range_]    
            range_start = range_[0] % count 
            range_end = range_[1] % count

        if range_end  <= range_start : 
            
            logger.critical(f'Invalid Range:: (range_start , range_end). Cannot operate on this')
            return False 

        cfg.DB.create_function('len' , 1 , len)

        stats = snowflake_driver.ranger(cfg.DBCursor , wordlist , range_start , range_end)    
        snowflake_driver.edit_meta(DBCursor , wordlist)
        snowflake_driver.produce_edit_stats(stats)
        #recount(wordlist)
        
        return True 
    
    elif re.match(r'^\>\d+$' , snowflake):
        
        len_min = snowflake[snowflake.find('>')+1:].strip()
        len_min = int((len_min))
        
        snowflake_driver.len_filter(cfg.DBCursor, wordlist , len_min)
        
    elif re.match(r'^\s*\<\d+\s*$' , snowflake):

        len_max = snowflake[snowflake.find('<')+1:].strip()
        len_max = int((len_max))
        snowflake_driver.len_filter(cfg.DBCursor, wordlist , len_max = len_max)        
    
    elif re.match(r'^\s*\d+\<\<\d+\s*$' , snowflake):
        
        len_min = snowflake[:snowflake.find('<')].strip()
        len_min = int((len_min))
        len_max = snowflake[snowflake.rfind('<')+1:].strip()
        len_max = int((len_max))
    
        snowflake_driver.len_filter(cfg.DBCursor, wordlist , len_min , len_max)
    
    else :
        
        logger.error(f'Cannot parse snowflake_flag::{snowflake}. Shutting down process')
        return False 
           
def delete(wordlist):
    
    if wordlist not in cfg.Wordlists:
        
        logger.error(f'Wordlist `{wordlist}` does not exist in database')
        return False 
        
    logger.critical(f'Executing DELETE')
    cfg.DBCursor.execute('begin')
    cfg.DBCursor.execute(f'DROP TABLE {wordlist}')
    cfg.DBCursor.execute('commit')
    
    logger.info(f'Successfully Deleted `{wordlist}`')
    
    cfg.DBCursor.execute("begin")
    cfg.DBCursor.execute('DELETE FROM wordlists WHERE name = ?' , (wordlist , ))
    cfg.DBCursor.execute('commit')
    
    logger.info(f'Successfully deleted metadata of `{wordlist}`')
    return True 

def list_make():
    
    import termcolor, colorama
    colorama.init(autoreset = True)
    
    vals = cfg.DBCursor.execute('SELECT name, description FROM wordlists').fetchall()
    
    if len(vals) == 0:
        
        logger.critical(f'No tables in the database to list')
        return False 
    
    lmax = len(max(vals , key = lambda x : len(x[0]) )[0]) % os.get_terminal_size().columns 
    
    termcolor.cprint('Name'.jlust(lmax) , end = '' , color = 'cyan')
    print(' : ' , end = '' )
    termcolor.cprint('Description' , color = 'yellow')
    
    for name , description in vals:
        termcolor.cprint(name.ljust(lmax) , end = '' , color = 'yellow')
        print(' : ' , end = '')
        termcolor.cprint(description , color = 'green')        
        
    colorama.deinit()
    return len(vals)

def copy(source , target):  
    
    if target in cfg.Wordlists:
        raise ValueError(f"Target Wordlist `{target}` already exists in the database")
    
    elif target.lower().startswith('temp') or target.lower().endswith('temp'):
        
        raise ValueError(f'Target Wordlist cannot start or end with temp due to operational reasons')

    elif target.strip().lower() == 'wordlists':
        
        raise PermissionError(f'Target wordlist cannot be `wordlists` due to intenal reasons')
    
    elif not re.match('^[\w|\_]+$' , target):
        
        raise ValueError(f'Target Wordlist can only have letters, digits and underscore')
    
    elif source not in cfg.Wordlists:
        raise ValueError(f'Source wordlist `{source}` not in the database')
    
    DBCursor.execute(f'CREATE TABLE {target} AS SELECT * FROM {source}')
    description , total_words = DBCursor.execute(f'SELECT description , total_words FROM wordlists WHERE name = ?' , (source , )).fetchone()
    
    DBCursor.execute(f'INSERT INTO WORDLISTS (name , description , total_words) VALUES (? , ? , ?)' , (target , description , total_words))
    DBCursor.execute('commit')
    
    logger.info(f'Successfully copied wordlist `{source}` to wordlist `{target}`')
 
def concat(sources , target , description):
    
    DBCursor.execute('begin')
    
    if target in cfg.Wordlists:
        
        logger.critical(f'Will append to existing target wordlist `{target}`')
        
    elif target.lower().startswith('temp') or target.lower().endswith('temp'):
        
        raise ValueError(f'Target Wordlist cannot start or end with temp due to operational reasons')
    
    elif target.strip().lower() == 'wordlists':
        
        raise PermissionError(f'Target wordlist cannot be `wordlists` due to intenal reasons')
    
    elif not re.match('^[\w|\_]+$' , target):
        
        raise ValueError(f'Target Wordlist can only have letters, digits and underscore')
    
    else:
        
        DBCursor.execute(f'CREATE TABLE {target}(word TEXT PRIMARY KEY ON CONFLICT IGNORE);')
        DBCursor.execute(f'INSERT INTO wordlists (name , description ) VALUES (? , ?)' , (target , f'Concatenation of {",".join(sources)}'))
    
    for source in sources:
        DBCursor.execute(f"INSERT INTO {target} SELECT word FROM {source}")   
        logger.info(f'Successfully concatenated {source} to {target} wordlist')
        
    total_items = DBCursor.execute(f'SELECT COUNT(*) FROM {target}').fetchone()[0]
    
    if description is None:
        description = f"Producing Concatenation of {tuple(sources)}"
    
    
    DBCursor.execute('  UPDATE wordlists \
                        SET updated_at = CURRENT_TIMESTAMP , total_words = ? , description = ?  \
                        WHERE name = ?' , (total_items , description , target))
    DBCursor.execute('commit')
    
    logger.info(f'{sources} successfully concatenated to {target}')
    #recount(target)
    
    return True 

def freeze(wordlist , output):
    
    if output is None:
        stream = sys.stdout
        
    else:
        stream = open(output , 'w' , encoding = 'utf8')

    logger.info(f'Will print to :: {stream}')
    n = 0 
    
    for word, *_ in cfg.DBCursor.execute(f'SELECT word FROM {wordlist}'):
        print(word, file = stream)       ##Not list comprehension to avoid memory usage
        n += 1 
    
    logger.info(f'Successfully printed {n} entries')
        
    if output is not None:
        stream.close()

def DriverMain(options : Namespace):
    
    if options.action in SNOWFLAKE_ALIASES:
        
        file = os.path.join(cfg.ProgPath , 'snowflake.md')
        data = open(file , 'r' , encoding = 'utf8').read()
        
        try:
            from rich.console import Console
            from rich.markdown import Markdown
            
            logger.info(f'Open `{file}` or `{file.replace(".md" , ".pdf")}` files to read more on the snowflake flag')
            console = Console()
            md = Markdown(data)
            console.print(md)
             
        except ImportError:
            
            logger.error(f'Open `{file}` or `{file.replace(".md" , ".pdf")}` files to read more on the snowflake flag')
            print(data)
            
        except:
            
            raise 
    
        return None 
            
    if options.action in GENERATE_ALIASES:
        
        logger.info('Executing CREATE')
        create(options.wordlist , options.file , options.words , options.description)
        recount(options.wordlist)
        return None 

    elif options.action in EDIT_ALIASES:
        
        logger.info('Executing EDIT')
        edit(options.wordlist , options.file , options.words, options.snowflake , options.description)
        recount(options.wordlist)
        return None 
        
    elif options.action in DELETE_ALIASES:
        
        [delete(wordlist) for wordlist in options.wordlist]
        return None 
        
    elif options.action in SHOW_ALIASES:
           
        [show(wordlist) for wordlist in options.wordlist]
        return None 

    elif options.action in COPY_ALIASES:
        
        copy(options.wordlist , options.target)
        recount(options.target)
        return None 
        
    elif options.action in CONCAT_ALIASES:
        
        concat(options.wordlist , options.target , options.description )
        recount(options.target)
        return None 
    
    elif options.action in FREEZE_ALIASES:
        
        return freeze(options.wordlist , options.output)
        
    elif options.action in LIST_ALIASES:
        
        return list_make()
    
    elif options.action in RECOUNT_ALIASES:
        
        [recount(wordlist) for wordlist in options.wordlist]
        return None 
       
    elif options.action in BACKUP_ALIASES:
        
        import sqlite3 
        bdb = sqlite3.connect(options.output)
        bcursor = bdb.cursor()
    
        bcursor.execute("begin")
        
        try:
            b = '\\'
            
            bcursor.execute(f"ATTACH DATABASE '{cfg.DBFile.replace(b , '/')}' as db_og")
            [bcursor.execute(f"CREATE TABLE {wordlist} AS SELECT * FROM db_og.{wordlist}") for wordlist in options.wordlist] 
            
            bdb.create_function('og_member' , 1 , lambda x : x in options.wordlist )
            bcursor.execute(f'CREATE TABLE wordlists AS SELECT * FROM db_og.wordlists WHERE og_member([name]);')
            
            bcursor.execute(f'UPDATE wordlists SET updated_at = CURRENT_TIMESTAMP;')      

            
        except sqlite3.Error as e :
            
            bcursor.execute("rollback")
            logger.error(f'Backup Operation Failed due to {e}')
            raise 
        
        except:
            raise 
        
        bcursor.execute("commit")
        logger.info("Backup Operation Successfully completed")
        return None 
   
    elif options.action in RESTORE_ALIASES:
        
        cfg.DBCursor.execute('begin')
        path = options.file.replace('\\' , '/')
        cfg.DBCursor.execute(f'ATTACH DATABASE "{path}" as db_restore;')
        
        try:
            
            if options.wordlists is None:
                
                options.wordlists = cfg.DBCursor.execute(f'SELECT [name] from db_restore.wordlists').fetchall()
                options.wordlists = [l[0] for l in options.wordlists]
                logger.info(f'Selecting All Wordlists from Restoration File:: {options.wordlists}')
            
            
            cfg.DB.create_function('og_member' , 1 , lambda x : x in options.wordlists )
            
            members = cfg.DBCursor.execute('select [name] from wordlists where og_member([name]);').fetchall()
            members = [m[0] for m in members]
            
            [cfg.DBCursor.executescript(f'DROP TABLE IF EXISTS {wordlist};CREATE TABLE {wordlist} AS SELECT * FROM db_restore.{wordlist}') 
                            for wordlist in options.wordlists]

            [cfg.DBCursor.execute(f'UPDATE wordlists SET updated_at = CURRENT_TIMESTAMP, total_words = ? WHERE [name] = ?;' , 
                             (cfg.DBCursor.execute(f'SELECT COUNT(*) FROM db_restore.{wordlist}').fetchone()[0] , wordlist))
                            for wordlist in members] 
            
            vals = [cfg.DBCursor.execute('SELECT [name] , total_words, [description] FROM db_restore.wordlists WHERE [name] = ? ' , (wordlist , )).fetchone()
            for wordlist in set(options.wordlists).difference(set(members))]
            
            cfg.DBCursor.executemany(f'INSERT INTO wordlists ([name] , [total_words], [description]) VALUES (?,?,?)' ,vals)  
            
            
        except:
            
            logger.error(f'Restore Operation Failed;')
            cfg.DBCursor.execute('rollback')
            raise 
        
        cfg.DBCursor.execute('commit')
        [recount(wordlist) for wordlist in options.wordlists]
        return None 
        
    elif options.action in HISTOGRAM_ALIASES:
        
        from .histograms import histogram_by_length
        
        if options.graphic:
            mode = 'graph'
        
        elif options.tabular:
            mode = 'tabular'
            
        else:
            mode = 'handle' 
        
        histogram_by_length(cfg.DBCursor , options.wordlist , mode, options.output)
        return None 
    
    elif options.action in SCRAPER_ALIASES:
        
        from . import scraper, snowflake 
        
        if options.responsive:
            logger.info('Executing Scraper in Responsive Mode; Will Use Selenium Driver')
            driver = scraper.get_driver()
            logger.info('Selenium Driver Successfully Initialized')
            func = lambda url : scraper.retrieve_selenium(url , driver)
        
        else:
            
            func = scraper.retrieve_soup
            
        for link in options.links:
            
            words = clean( func( link) )
            logger.info(f'Scraped {len(words)} words from {link}')
            edit_stats = snowflake.add(cfg.DBCursor , options.wordlist , None , words)
            snowflake.produce_edit_stats(edit_stats)
        
        recount(options.wordlist)
        return None 
    
if __name__ == '__main__':
    
    import coloredlogs, pretty_traceback
    pretty_traceback.install()
    coloredlogs.install(fmt = '[%(name)s] %(asctime)s %(levelname)s :: %(message)s')
    DriverMain(arguments())