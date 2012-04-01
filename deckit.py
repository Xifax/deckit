#!/usr/bin/python
# coding: utf-8
''' CLI utility to compile Anki-compatible english-english decks.
    Uses Wordnik API (unique user api key required - one can get it at wordnik.com).
    Should work both on -nix and Windows compatible OS.
    Requires python and some of its modules (or pip/setuptools to install those).

    tl;dr: python script, looks up words online, compiles anki deck with the results, english only
    
    Usage: ./deckit do wordnik_key words_in deck_out

    -> General purpose:
    Easily prepare english to english Anki decks for large unformatted lists of unknown vocabulary.

    -> Input file format:
    <-- words start from here -->
    foo
    bar
    baz
    /*zug*/

    -> Resulting card format:
        word
        reading
        ----
        meanings
        phrases
        examples

    Compiled text files should be imported in Anki (either in new or existing decks).

    -> Notes:
    * for card front some unicode-compatible font should be used (phonetic symbols), e.g. Gentium Plus
    * only two fields are in resulting import txt: front and back; no tags included;
    
    -> What could be done better:
    * better coloring scheme (may be some suave tones, instead of generic ones);
    * batch-processing for Wordnik requests (it's soooooo sloooooow);
    * definition field tweaks: part of speech/dictionary coloring;
    * better windows compatibility;

    -> What (definitely) ought to be done: 
    * required modules installation procedure, using this very script (as of now - broken);
  
    -> Possible bugs:
    * Words (card_front) with non-ascii characters
    * Empty fields
    
'''
__author__ = 'Artiom Basenko'
__email_ = 'demi.log@gmail.com'
__license__ = 'GPL'
__version__ = '0.9'

import sys
import traceback
#import logging
from ordereddict import OrderedDict

try:
  from argh import arg, ArghParser
  from wordnik import Wordnik
  from clint.textui import progress, colored, puts
except ImportError:
  sys.exit('Required packages [argh, wordnik, clint] are not installed!')

def oops(message):
    ''' Show error message and quit'''
    puts(colored.red(message)) or sys.exit(1)

class Lookup:
    ''' Looks up different stuff on Wordnick
        NB: no batch-processing - very slow!
        TODO: do batch-processing (using Wordnik.multi)?
    '''

    def __init__(self, api_key):
      '''Initialize and check wordnik apu key'''
      puts(colored.blue('Using Wordnik API key: %s' % api_key))
      self.w = Wordnik(api_key)
      try:
          if(self.w.account_get_api_token_status()['valid']):
              puts(colored.green('OK, API key is valid. Commencing lookup (it may take a while)...'))
      except TypeError:
          raise Exception ('Wrond API key!')

    def define(self, word):
      '''Get all available definitions'''
      # TODO: add part of speech (in blue?)
      # TODO: gray out 'Informal', 'Slang', 'Naval' and such
      definitions = self.w.word_get_definitions(word)
      card_define = ''
      for definition in definitions:
          if 'text' in definition:
              card_define += definition['text'] + u'<br />'
      return card_define

    def example(self, word):
      '''Get example sentences'''
      # TODO: no more than 3-4 examples (sorted by highest score!)
      examples = self.w.word_get_examples(word)
      card_example = ''
      if 'examples' in examples:
        # Use no more than 4 example sentences (or as limit for w_g_examples())
        for example in examples['examples'][:4]:
          if 'text' in example:
              card_example += example['text'].replace(word, Decker.bold(word)) + u'<br />'
      return card_example

    def pronounce(self, word):
      '''Get pronounciation (in round brackets)'''
      pronunciations = self.w.word_get_pronunciations(word)
      if(pronunciations):
          try:
              return pronunciations[0]['raw']
          except Exception:
              return u''
    
    def phrase(self, word):
      '''Get phrases with this word'''
      phrases = self.w.word_get_phrases(word)
      card_phrase = []
      for phrase in phrases:
        try:
          card_phrase.append(phrase['gram1'] + ' ' + phrase['gram2'])
        except Exception:
          pass
      if(card_phrase):
        return ' | '.join(card_phrase) + u'<br />'

    def batch(self, words):
      '''Batch lookup. Note, that it not always works as it should.'''
      calls = []
      requests = ['definitions', 'examples', 'phrases', 'pronounciations']
      for word in words:
        for request in requests:
          calls += (word, request)
      return Wordnik.multi(calls)
      
class Decker:
    ''' Compiles dictionary of cards from Lookup'er
        to Anki-compatible text import
    '''

    def __init__(self, cards, file_out):
        '''Create and save deck txt import file'''
        self.cards, self.deck = cards, file_out
        self.save()
        
    @staticmethod
    def span(string, color = 'gray'):
        '''Color the text (note, that ";" should not be used in tags)'''
        return '<span style="color:%s">%s</span>' % (color, string)

    @staticmethod
    def bold(string):
      '''Add emphasis to text (note: span is better but more troublesome)'''
      return '<b>%s</b>' % string

    def save(self):
        '''Convert dictionary of words and definitions to fit Anki format'''
        puts(colored.blue('Constructing import deck...'))
        # Shortcut for chopping substrings from the end of string (rstrip, somehow, works bad)
        chop = lambda string, ending: string[:-len(ending)] if string.endswith(ending) else string

        output = open(self.deck, 'w')
        #for card_front, card_back in progress.bar(self.cards.items()):
        for card_front, card_back in self.cards.iteritems():
          try:
            #print card_front
            # Front of a card: word itself + pronounciation (if any)
            # TODO: check for non-ascii symbols
            # TODO: exclude items without definitions and examples
            import_line = card_front
            if(card_back['pronounce']):
              import_line += u'<br />' + Decker.span(card_back['pronounce'])
              del(card_back['pronounce'])
            import_line += u';'
              
            # Back of a card: definitions, examples, phrases (separated by horizontal lines)
            for name, field in card_back.iteritems():
              # Let's add some colors!
              if(field):
                  if(name == 'example'):
                    field = Decker.span(field, 'purple')
                  if(name == 'phrase'):
                    field = Decker.span(field, 'green')
                  import_line += field.replace(';', ',') + u'<hr />'
              # Removing <br /> before <hr />
              import_line = import_line.replace(u'<br /></span><hr />', u'</span><hr />')
            # Chopping the last horizontal line
            import_line = chop(import_line, u'<hr />')
            # Write new card suitable for import
            output.write('%s\n' % import_line.encode('utf-8'))
          except Exception, e:
            #oops('Could not write a card: %s for word"%s"' % (e, card_front.encode('utf-8')))
            oops('Could not write a card: %s' % e)
            traceback.print_stack()
        puts(colored.green('Deck compilation complete! You may now import resulting "%s" file using Anki.' % self.deck))

#TODO: make it work as it should!
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
@arg('deck_out', default="deck", help='text file to import (anki compatible)')
def do(args):
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
            # Skip lines starting with '/*'
            if(not line.startswith('/*')):
              new_words.append(line.strip('\r\n'))
        # Separator ought to be at the beginning of the file or somewhere else
        if line.startswith('<--') and line.strip('\r\n').endswith('-->'):
            new_words_began = True

    # 3. Compile definitions and examples as deck cards
    cards = {} 
    try:
        for word in progress.bar(new_words):
          cards[word] = OrderedDict([ 
                          ('define',    lookup.define(word)),
                          ('phrase',    lookup.phrase(word)),
                          ('example',   lookup.example(word)),
                          ('pronounce', lookup.pronounce(word))
                        ])
    except Exception as e:
        oops('Some problem with Wordnik arised: %s' % e)
        traceback.print_stack()

    # 4. Save to Anki import-compatible text file
    try:
        Decker(cards, args.deck_out)
    except Exception as e:
        oops('Could not write resulting deck: %s' % e)
        traceback.print_stack()

if __name__=='__main__':
    # As of now, will work with argh only - not good
    p = ArghParser()
    p.add_commands([do, install])
    p.dispatch()
