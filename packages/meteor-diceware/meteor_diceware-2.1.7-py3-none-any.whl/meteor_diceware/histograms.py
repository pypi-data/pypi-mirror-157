def table_print(vals):
    
    from tabulate import tabulate 
    print(tabulate(vals , headers = ['WordCount' , 'Words'] , tablefmt = 'grid'))

def graph_make(vals):
    
    import plotext as tpl
    
    vals = vals[:-1]
    x, y = zip(*vals)
    tpl.bar(x , y )
    tpl.xlabel('Length of Word')
    tpl.ylabel('No of words')
    tpl.show()

def csv_write(vals, file):
    
    import csv
    
    with open(file , 'w' , encoding = 'utf8') as handle:
        
        writer = csv.writer(handle)
        writer.writerow(['WordLength' , 'Words'])
        writer.writerows(vals)
        
    return None 

def histogram_by_length(cursor , wordlist, mode , file = None):
    
    vals = cursor.execute(f'SELECT length(word) as WordLength , count(*) as WordCount FROM {wordlist} GROUP BY WordLength').fetchall()
    total = sum([x[1] for x in vals])
    vals.append(['Total' , total])
    
    if mode in ('table' , 'tabular'):
        
        table_print(vals)
        
    elif mode == 'graph':
        
        graph_make(vals)
        
    elif mode == 'handle':
        
        if file is None:
            file = 'histogram.csv'
        
        csv_write(vals , file)
        
        
    else:
        print(mode)