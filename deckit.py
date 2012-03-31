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
from ordereddict import OrderedDict

try:
  from argh import arg, ArghParser
  from wordnik import Wordnik
  from clint.textui import progress, colored, puts
except ImportError:
  sys.exit('Required packages [argh, wordnik, clint] are not installed!')

def oops(message):
    ''' Show error message and quit'''
    puts(colored.red(message))
    sys.exit(1)

class Lookup:
    ''' Looks up different stuff on Wordnick
        NB: no batch-processing - very slow!
        TODO: do batch-processing?
    '''

    def __init__(self, api_key):
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
      # TODO: no more than 3-4 examples (sort by highest score!)
      examples = self.w.word_get_examples(word)
      if 'examples' in examples:
        card_example = ''
        for example in examples['examples']:
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
      
class Decker:
    ''' Compiles dictionary of cards from Lookup'er
        to Anki-compatible text import
    '''

    def __init__(self, cards, file_out):
        '''Create and save deck txt import file'''
        self.cards = cards
        self.deck = file_out
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
        # Shortcut for chopping substrings from the end of string (rstrip, somehow, works bad)
        chop = lambda string, ending: string[:-len(ending)] if string.endswith(ending) else string

        output = open(self.deck, 'w')
        for card_front, card_back in self.cards.iteritems():
          # Front of a card: word itself + pronounciation (if any)
          import_line = card_front
          if(card_back['pronounce']):
            import_line += u'<br />' + Decker.span(card_back['pronounce'])
            del(card_back['pronounce'])
          import_line += u';'
            
          # Back of a card: definitions, examples, phrases (separated by horizontal lines)
          for name, field in card_back.iteritems():
            # TODO: sort keys as : definition, examples, phrases
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
            # Skip lines starting with '/*'
            if(not line.startswith('/*')):
              new_words.append(line.strip('\r\n'))
        # Separator ought to be at the beginning of file or somewhere else
        if line.startswith('<--') and line.strip('\r\n').endswith('-->'):
            new_words_began = True

    # 3. Compile definitions and examples as deck cards
    cards = {} 
    try:
        for word in progress.bar(new_words):
          cards[word] = OrderedDict({ 
                          'define'    : lookup.define(word),
                          'phrase'   : lookup.phrase(word),
                          'example'   : lookup.example(word),
                          'pronounce' : lookup.pronounce(word),
                        })
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
