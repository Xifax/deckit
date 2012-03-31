deckit<br />
Python script to quickly convert list of (eng) words to text file with (eng-eng) examples and definitions, [suitable] for [Anki] import.
All words are processed using [Wordnik]

---

Installation:

    python deckit install

Usage:

    python deckit process key words deck
    
or

    ./deckit process key words deck
    
Notes:

* Requires **Python** 2.7
* Also requires:
    * argh
    * wordnik
    * clint
* One should get api key from [Wordnik]


[Anki]: http://ankisrs.net/ 
[suitable]:  http://ankisrs.net/docs/FileImport.html
[Wordnik]: http://www.wordnik.com/ 
