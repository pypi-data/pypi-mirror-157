CREATE TABLE wordlists (

    pk INTEGER PRIMARY KEY,
    name TEXT,          -- Default Name of Wordlist 
    description TEXT,   -- Description for Wordlist 
    total_words INTEGER DEFAULT 0, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(name)

);
