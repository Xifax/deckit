#!/usr/bin/python
# coding: utf-8
''' CLI utility to complie anki english-english decks.
    Uses Wordnik API (api key required).

    Resulting card format:
        word
        ----
        thesaurus meaning (or several of those)
        examples
        phrases
        readings

    Compiled text files should be imported in Anki (in new or existing decks).
'''
import sys

from argh import arg, ArghParser
from wordnik import Wordnik
from clint.textui import progress

def oops(message):
    ''' Show error message and quit'''
    sys.exit(message)

class Lookup:
    ''' Looks up different stuff on Wordnick
        NB: no batch-processing - very slow!
    '''

    def __init__(self, api_key):
        print 'Using Wordnik API key: ', api_key
        self.w = Wordnik(api_key)
        try:
            if(self.w.account_get_api_token_status()['valid']):
                print 'OK, API key is valid. Commencing lookup (it may take a while)...'
        except TypeError:
            raise Exception ('Wrond API key!')

    def define(self, word):
        definitions = self.w.word_get_definitions(word)
        card_define = ''
        for definition in definitions:
            if 'text' in definition:
                card_define += definition['text'] + u'<br />'
        return card_define

    def example(self, word):
        examples = self.w.word_get_examples(word)
        card_example = ''
        for example in examples:
            if 'text' in example:
                card_example += example['text'] + u'<br />'
        return card_example

    def pronounce(self, word):
        pronunciations = self.w.word_get_pronunciations(word)
        if(pronunciations):
            try:
                return pronunciations[0]['raw']
            except Exception:
                return u'[]'

class Decker:
    ''' Compiles dictionary of cards from Lookup'er
        to Anki-compatible text import
    '''

    def __init__(self, cards, file_out):
        self.cards = cards
        self.deck = file_out
        self.save()

    def save(self):
        output = open(self.deck, 'w')
        for card_front, card_back in self.cards.iteritems():
            import_line = card_front + u';'
            for field in card_back.values():
                if(field):
                    import_line += field + u'<hr />'
            import_line.rstrip('<hr />')
            output.write('%s\n' % import_line.encode('utf-8'))
        print 'Deck compilation complete! You may now import resulting "%s" file using Anki.' % self.deck

def install(args):
    "Install all required python modules using pip/easy_install (should be run as root)"
    packages = ['wordnik', 'argh', 'clint']
    try:
        import pip
        pip.main(['install'] + packages)
        sys.exit(0)
    except ImportError:
        try:
            from setuptools.command import easy_install
            for package in packages:
                easy_install.main(['-U', package])
        except ImportError:
            oops('Please, install either pip or setuptools')

@arg('api_key', default="key", help='text file with wordnik api key (first line)')
@arg('file_in', default="words", help='text file with words (separated by line)')
@arg('deck_out', default="deck", help='text for deck import (anki compatible)')
def process(args):
    "Process text file with words, generate text suitable for Anki import"
    # 1. Get Wordnik api key
    try:
        lookup = Lookup(open(args.api_key).readline().strip(' \r\n'))
    except Exception as e:
        oops('There was a problem with Wordnik: %s' % e)

    # 2. Process file with words to add to deck
    new_words_began = False
    new_words = []
    for line in open(args.file_in):
        # Skip the words before the separator
        if(new_words_began):
            new_words.append(line.strip('\r\n'))
        # Separator ought to be at the beginning of file or somewhere else
        if line.startswith('<--') and line.strip('\r\n').endswith('-->'):
            new_words_began = True

    # 3. Compile definitions and examples as deck cards
    cards = {}
    try:
        for word in progress.bar(new_words):
            cards[word] = { 'define'    : lookup.define(word),
                            'example'   : lookup.example(word),
                            'pronounce' : lookup.pronounce(word)
                          }
    except Exception as e:
        oops('Some problem with Wordnik arised: %s' % e)

    # 4. Save to Anki import-compatible text file
    try:
        Decker(cards, args.deck_out)
    except Exception as e:
        oops('Could not write resulting deck: %s' % e)

if __name__=='__main__':
    p = ArghParser()
    p.add_commands([process, install])
    p.dispatch()
