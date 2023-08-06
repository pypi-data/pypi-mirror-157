## Snowflake Flag and Uses

The edit flag, also called Snowflake flag for ```meteor_diceware``` is an edit flag with the following possible options:

1. Add entries 

```python3 
python3 -m meteor_diceware.utils edit <wordlist> --snowflake + -f <filetoaddfrom> -w <word_1> <word_2> .... <word_n>
```

This adds the words in _`<filetoaddfrom>`_ and the list of words supplied to _`-w`_ flag to the existing words in the _`<wordlist>`_

2. Remove entries 

```python3
python3 -m meteor_diceware.utils edit <wordlist> --snowflake - -f <filetosubtractfrom> -w <word_1> <word_2> .... <word_n>
``` 

This subtracts the words in _`<filetoaddfrom>`_ and the list of words supplied to _`-w`_ flag from the existing words in the _`<wordlist>`_. 
<div style="page-break-after: always;"></div>

3. Slicing Operator for Filtering Entries 

```python3 
python3 -m meteor_diceware.utils edit <wordlist> --snowflake 1: 
```

Snowflake flags of this kind filter out the words stored. It is similar to the python range operator and the following can be used. It filters out entries based on length of strings:

<table width="100%">
 <tr>
  <th align='centre'> Flag
  <th align='centre'> Slice Meaning
  </tr> 
  <tr>
    <td> n:      
      <td> Removes n smallest(by length) entries  
  </tr>
  <tr>
    <td> :n 
      <td> Keeps only n smallest(by length) entries 
  </tr> 
  <tr> 
    <td> -n:
      <td> Keeps only n largest(by length) entries 
  </tr>
  <tr>
    <td> :-n
      <td> Removes n smallest(by length) entries
  </tr>
  <tr>
    <td> 
      m:n
      <td> Removes the m smallest entries and keeps the next n-m entries, deleting the ones larger than those m entries 
  </tr> 
  </table> 

4. Filtering Based on Length

This uses a slightly different type of operator, and uses the following syntax
<table align='center' width="100%">
  <tr>
    <th> Flag
      <th> Comparator Meaning
  </tr>
  <tr>
    <td> `>m`
	<td>  Words In length greater than M only 
  </tr>
  <tr>
    <td> `&lt;n` 
      <td> Words in length less than N only 
  </tr>
  <tr>
    <td> `m&lt;&lt;n`
      <td> Words in length greater than M and less than N only 
</table>
  

5. Editing Description only 

To edit the description only of the entry, use the empty string for the snowflake flag. 

```python3 
python3 -m meteor_diceware.utils edit <wordlist> --snowflake "" --description <newdescription>
``` 

This adds the description to the database 