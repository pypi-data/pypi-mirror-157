## Meteor Diceware 
A low-resource, easy to use, low latency, customizable and cryptographically secure implementation of [Diceware](https://en.wikipedia.org/wiki/Diceware) which uses a single database which can populate millions of entries for possible words and can easily generate cryptographically strong and secure passwords which one can easily remember. 

#### Installation 

The package has not yet been uploaded to PyPI, and hence needs to be built from source. 

```
git clone  https://gitlab.com/loggerheads-with-binary/meteor_diceware.git 
cd meteor-diceware 
python3 -m pip install -r requirements.txt 
python3 setup.py install 
```

**Note: The utility already comes with the original diceware list as the wordlist `main`. Other wordlists can be inserted manually through files or via the command line** 

#### Use cases 

It's always advised to use >= 5 words for the password as well as to use >=2 special characters. To establish the same, one can do the following:

Ex: 
```
$ python3 -m meteor_diceware -n 5 -d "_" -s 2 
> For_2Says_For_Ch8aracters_Is  
```

NOTE :: Please do not use diceware and then make obvious substituions like changing SANA to $^N^. It has been proven time and again that **addition**, not substitution is what makes a password more cryptographically secure. As in `MALO0NE` is more secure than `MAL0NE`

#### Using utils 

`meteor_diceware.utils` is a bundled accessory which helps generate, edit, delete, concatenate, backup and maintain wordlists. 

The following actions can be performed via the utils command-line:

1. `python3 -m meteor_diceware.utils create <wordlistname> -w <word1> <word2>... -f <text file to pull words from>` : As obvious this generates a new wordlist by the name `<wordlistname>`
2. `utils edit <wordlistname> -w <word1> <word2> ... -f <file>` : It adds words to an existing database 
*Note: Check more on using the snowflake flag in the file snowflake.pdf* 
3. `utils show <wordlistname>` : Shows summary and content information of the wordlist 
4. `utils freeze <wordlistname> -o <file>` : Outputs all the words from the wordlist in the text file `<file>`
5. `utils rm <wordlist1> <wordlist2> ...` : Remove one or more wordlists from the database
6. `utils ls` : Lists all the existing wordlists from the database
7. `utils cp <wordlist> -t <target>` : Copies wordlist to target within the database. Can be used as a backup of some sort
8. `utils cat <wordlist1> <wordlist2> .... -t <target>` : Concatenates files from all the different wordlists to the target wordlist
9. `utils recount <wordlist1> <wordlist2> ...` : Rebases and reindexes the wordlists. This counter/index is used internally within the program and is not exposed to the user.
10. `utils backup <wordlist1> <wordlist2> ... -o <file>` : Creates a copy of the wordlists into a separate SQLite Database file `<file>`
11. `utils restore <file> -W <wordlist1> <wordlist2> --replace` : Restores wordlists from a separate file to the main database 
12. `utils histogram <wordlist> --graphic/--tabular/--output <file>` : Creates a length histogram of the words in the wordlist and presents in both tabular and graphic form. Can also be exported to `.csv` format if -o flag is used.
13. `utils scrape <wordlist> --links <link1> <link2> ... ` : Scrape the links and add the words to the wordlist. Use `--responsive` flag for responsive pages and use selenium. 

#### Credits 

The following [Diceware Words List](https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt) has been used as-is to create the main wordlist of the program. 

#### Bugs 

Any bugs or cryptographic suggestions can be sent to [dev@aniruddh.ml](mailto:dev@aniruddh.ml)  