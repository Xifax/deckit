deckit
======

*Python script to quickly convert list of (eng) words to text file with (eng-eng) examples and definitions*, [suitable] for [Anki] import.<br />
All words are processed using [Wordnik], so *one should aquire unique api key*.<br /> Usually finds definitions (or, at least, examples) even for the most obscure lexicon.<br />
*Plain text output format* over anki deck was chosen due to versatility of anki import (e.g., depending on the model, the same two-fields text could be imported differently).

---

Installation:

    python deckit.py install

Usage:

    python deckit.py do key words deck
    
or

    ./deckit.py do key words deck
    
Notes:

* Requires **Python** 2.7.X
* Also requires (all dependencies may be installed right from the script itself):
    * argh
    * wordnik
    * clint
    * ordereddict
* One should get api key from [Wordnik]
* In case there's alternative/unusual spelling specified, definition will likely say so

Todo:

* Batch-processing
* Additional field for all the optional information (dictionary, part of speech, etc)

[Anki]: http://ankisrs.net/ 
[suitable]:  http://ankisrs.net/docs/FileImport.html
[Wordnik]: http://www.wordnik.com/ 
