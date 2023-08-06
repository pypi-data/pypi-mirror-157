CREATE TABLE wordlists (

    pk INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT, -- Description for Wordlist 
    total_words INTEGER DEFAULT 0, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
 
);
