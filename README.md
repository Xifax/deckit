deckit
======

Python script to quickly convert list of (eng) words to text file with (eng-eng) examples and definitions, [suitable] for [Anki] import.<br />
All words are processed using [Wordnik], so one should aquire unique api key.

---

Installation:

    python deckit install

Usage:

    python deckit do key words deck
    
or

    ./deckit do key words deck
    
Notes:

* Requires **Python** 2.7
* Also requires:
    * argh
    * wordnik
    * clint
* One should get api key from [Wordnik]

Bugs and glitches:

* Problems with non-ascii symbols
* Blank cards


[Anki]: http://ankisrs.net/ 
[suitable]:  http://ankisrs.net/docs/FileImport.html
[Wordnik]: http://www.wordnik.com/ 
