#### SKIP ALL THE CORPUS CRAP -- YOU DON'T NEED IT FOR Bag of Words Stuff###
# https://github.com/cltk/tutorials
#http://docs.cltk.org/en/latest/importing_corpora.html
#The trick to getting the Chrysostom corpus to download was to push the repo up to github and to create
#
#~/cltk_data/distributed_corpora.yaml with:
#real_chrysostom_corpus:
#   origin: git@github.com:classicist/real_chrysostom.git
#    language: greek
#    type: plaintext
#
#I also had to ducktape over a bug at cltk/corpus/utils/importer.py:307
#   git_name = 'fake_corpus_name_from_PAUL' #corpus_properties['']
# because corpus_properties[''] throws an error,
# git_name is only used in an error message on line 272
## Download corpus from github
# NOTE: This is a 1 time operation, if you have already downloaded it,
# Git will fail with a 128 error, because it can't make a new dir where a dir already exits,
# because you already fucking downloaded it there lastime!
## BETTER NOTE: All this does is copy the git repo to /Users/paul/cltk_data/greek/text/real_chrysostom_corpus
# Next time, just copy it over by hand and be done with it. So dumb.
##
# TODO: If I am nice, I should patch this for them
##
#from cltk.corpus.utils.importer import CorpusImporter
#corpus_importer = CorpusImporter('greek')
#corpus_importer.import_corpus('real_chrysostom_corpus')
#Get Chrysostom with FilteredPlainTextCorpusReader
# Now I had to manually add my corpus name to the dict at cltk/corpus/readers.py:31
#from cltk.corpus.readers import get_corpus_reader
#john_reader = get_corpus_reader(corpus_name = 'real_chrysostom_corpus', language = 'greek')
#len(list(john_reader.words())) # correct-ish!
#len(list(john_reader.docs())) # correct!
#len(list(john_reader.paras())) #useless! Splits on blank line, so it just registers 1 para / doc
####
## NOTES ON CLTK CODEBASE AND OPENSOURCE PROJECT
# The quality of this code is among the lowest you've seen on anything even semi-pro. Nowhere near production ready
# (but it's a 5+ year old project in v0.1.117 -- whatever that means!).
# 0 Tests, TONS of broken code, TONS of comments and TODOs litter the code like a wasteland.
# The most of the code looks like it was written by the worst kind of lazy Java developer, but for Python.
# Looking at the issues list on github, the community has no idea either how to code, or how to
# run a project. They also seem real defensive. I get bad vibes. Also, they are expanding and contracting at
# the same time -- they don't do Greek or Latin well, but they want to include *all* languages? Dumb.
# Lots of stuff is out of date too; e.g., the TLG Word2Vec models were last run 5 years ago (and probably badly tuned then).
# They are also talking about REMOVING support for TLG altogether bc they "don't want to encourage people to use closed sources."
# Dumb. Also, the docs are misleading -- they make it sound like you've got to
# Just to get the stuff below up and running took you 1/2 a day of debugging thier fucking non-sense. The only purpose of much of which
# was just to download text I already fucking had! The docs SUCK (and are wrong too!).
# THINK TWICE ABOUT CONTRIBUTING ANYTHING TO THESE FUCKTARDS. It will probably be more of a headache than it's worth
# Better just to copy/paste some of their code and start your own python project for Greek (dactyle?).
# No downloading bullshit, just language tools that work on strings of text, corpus readers that deal with words/para/sent and XML, and ML tools.
# All of it cutting-edge, rock-solid TDDed stuff. Build ML tools ontop of fastai.
####

### START HERE ###
# Fire up Python3.7 with all your goodies
# source venv/bin/activate
# Fire up your REPL
# ipython --log-level=DEBUG
# Drop everything else below in it
####

#0. Setup -- you did this already. If you have files in ~/cltk_data/... you're good.
#from cltk.corpus.utils.importer import CorpusImporter
# corpus_importer = CorpusImporter('greek')
# corpus_importer.import_corpus('greek_models_cltk') #downloads files from github to ~/cltk_data/...
# corpus_importer.import_corpus('greek_treebank_perseus') #downloads files from github to ~/cltk_data/...
# corpus_importer.import_corpus('greek_lexica_perseus') #downloads files from github to ~/cltk_data/...
# corpus_importer.import_corpus('greek_training_set_sentence_cltk') #downloads files from github to ~/cltk_data/...
# corpus_importer.import_corpus('greek_word2vec_cltk') #downloads files from github to ~/cltk_data/...
# TODO: the greek_word2vec_cltk github repo is broken for some reason and wont checkout. Open a ticket, if you feel nice. Errors are in the .git/logs error file.
# TODO: I fixed it by cloning the repo, then downloading
### Run cleanup_tlg_text.rb in editor
## Idempotent method to get a clean, single text at "all_johns_text_path"
####
# use goodness: https://ipython.org/ipython-doc/3/config/extensions/autoreload.html
%load_ext autoreload
%autoreload 2
#1. Read in text file, minimal cleaning for sanity
# hand selcted from words occuring > 1000x
#from collections import Counter
#counts = Counter(lemmata)
#print(counts)
most_common_empty_words_for_john = ['ὁ', 'καὶ', 'οὗτος', 'τὴν', 'οὐ', 'γὰρ', 'εἰμί', 'τὸ', 'δὲ', 'αὐτός', 'τὸν', 'ἐγώ', 'τὰ', 'ἐν', 'ὅστις', 'μὴ', 'ἀλλὰ', 'σύ', 'λέγω1', 'πᾶς', 'ἀλλ', 'εἰς', 'τίς', 'διὰ', 'μὲν', 'γίγνομαι', 'εἰ', 'τοὺς', 'πρὸς', 'οὕτως', 'ποιέω', 'ἔχω', 'ἐκεῖνος', 'εἶπον', 'ἐπὶ', 'οὐδὲ', 'ἂν', 'τις', 'ἵνα', 'μετὰ', 'ὡς', 'ἀπὸ', 'οὖν', 'αὐτὸν', 'μόνος', 'ἐκ', 'περὶ', 'ὁράω', 'φημί', 'πολύς', 'πως', 'μέγας', 'τὰς', 'πάλιν','ἕτερος', 'ἢ', 'ὅταν', 'οὐδὲν', 'ἀκούω', 'εἶδον', 'τοσοῦτος', 'ἅπας', 'τοιοῦτος', 'ἐπειδὴ', 'δέω1', 'ἑαυτοῦ', 'δείκνυμι', 'κἂν', 'αὐτοὺς', 'ἐνταῦθα', 'μᾶλλον', 'κατὰ', 'οἶδα', 'φησὶν', 'ἄλλος', 'δοκέω', 'λόγος', 'ὑπὲρ', 'παρὰ', 'νῦν', 'τότε', 'κύριος', 'δίδωμι', 'ὥστε', 'ὅς', 'φησὶ', 'λαμβάνω', 'τοίνυν', 'πρότερος', 'μέλλω', 'πρᾶγμα', 'αὐτὸς', 'δι', 'γαῖα', 'ὥσπερ', 'ἥμερος', 'παῦλος', 'καλέω', 'ἐρῶ', 'σῶμα', 'παρ', 'δὴ', 'ὅσος', 'οὔτε', 'καθά', 'μηδὲ', 'γάρ', 'αὐτὸ', 'αὐτὴν', 'τε', 'ἔρχομαι', 'νόμος', 'σὺ', 'ὑπὸ', 'φέρω', 'ῥῆμα', 'ἵστημι', 'ἐὰν', 'οἰκέω', 'ὅσπερ', 'ἐργάζομαι', 'ὃ', 'λοιπὸν', 'νομίζω', 'ἐκεῖ', 'ἐγὼ', 'ἐπιδείκνυμι', 'ἅγιος', 'ἁπλόω', 'εἶτα', 'ἕκαστος', 'πάρειμι1', 'ἐπάγω', 'μάλιστα', 'οὐχὶ', 'εἷς', 'ἡμέτερος', 'οὐρανός', 'διὸ', 'καθ', 'πρὸ', 'ἕνεκα', 'ὅστε', 'δέ', 'πολλάκις', 'πολλὴν', 'τίθημι', 'ἐντεῦθεν', '<', '>', 'αἰών', 'ἵημι', 'ποτέ', 'ἐπεὶ', 'ἐναντίος', 'ἑαυτὸν', 'διαλέγω', 'μηδὲν', 'καίτοι', 'γε', 'ποῖος', 'ἄγω', 'τοῦτό', 'μυρίος', 'πανταχοῦ', 'δηλόω', 'ἐννοέω', 'οὐδείς', 'αὐτὰ', 'ἀεὶ', 'ἀνά', 'πολλὰ', 'πόσος', 'οὐδεὶς', 'γοῦν', 'εἰπὼν', 'ἔτι', 'πλείων', 'ἐστὶ', 'τυγχάνω', 'οἷος', 'πόλις', 'εὐθύς', 'κελεύω', 'μετ',  'δῆλος', 'ἑαυτοὺς', 'ἐστὶν', 'μεθ', 'πράσσω', 'πολλοὶ', 'πού', 'ἀνίστημι', 'μακάριος', 'μικρὸν', 'ἐπ', 'μήτε', 'δύο', 'αὐτοὶ', 'ὅλοξ', 'ἀρκέω', 'δεικνὺς', 'μέχρι', 'ἠώς', 'κατ', 'ἃ', 'ἣν', 'ὃν', 'ὢν', 'ἰδοὺ', 'ἀντὶ', 'τουτέστιν', 'ἀλλήλων', 'ἄνω1', 'μή', 'ἐπιτυγχάνω', 'ἔσχατος', 'παντὸς','εἰσέρχομαι', "αὐτός", "ἐκεῖνος", "ἐνταῦθα","τοιοῦτος", "κενόω","οὖν","ποῖος","οὐδείς","οὐδαμός","ἐφ_","ἐφ",'ὅθεν',"πλὴν",'πολὺ','τουτέστι','ὅπου','ὅπως','οὐκοῦν','ἅμα','μὴν',"βʹ","αʹ","γʹ",'αγιοισ', 'δευτεραν','αρχιεπισκοπου', 'αρχιεπισκοπου_κωνσταντινουπολεωσ', 'εισ', 'εισ_την', 'την','εν', 'εν_πατροσ', 'πατροσ','επιστολην', 'ημων', 'ημων_ιωαννου','ιωαννου','«',":", "'",";",'!',]
from cltk.corpus.utils.formatter import cltk_normalize #try to see if it changes anything -- just wraps and feeds unicodedata.normalize(form, unistr)
all_johns_text_path = "/Users/paul/cltk_data/greek/text/real_chrysostom_corpus/ALL_REAL_JOHN_FOR_BAG_OF_WORDS.TXT"
file = open(all_johns_text_path)
words = file.read().lower() #lower_case everything upfront JIC; 21,049,531 words
normal_words = cltk_normalize(words) #crucial!
file.close()

#2. Tokenize
from cltk.tokenize.word import WordTokenizer
word_tokenizer = WordTokenizer('greek')
tokenized_words = word_tokenizer.tokenize(normal_words) #4,017,449 words; tokenized_words[-20:-1]

#3. Lemmatize Words
# changed = []; [changed.append(word) for word in set(tokenized_words) if word not in set(lemmata)]; print(changed); print(len(changed))
from cltk.stem.lemma import LemmaReplacer
lemmatizer = LemmaReplacer('greek')
lemmata = lemmatizer.lemmatize(tokenized_words)

#4. Remove Stop words (καί, δέ, ...) and Swadesh words ('ἐγώ', 'σύ', 'αὐτός, οὗ, ὅς, ὁ, οὗτος', 'ἡμεῖς', 'ὑμεῖς', 'αὐτοί',...)
from cltk.stop.greek.stops import STOPS_LIST
from cltk.corpus.swadesh import Swadesh
import numpy as np
swadesh_words = cltk_normalize(",".join(Swadesh('gr').words())).split(",")
stop_words = cltk_normalize(",".join(list(STOPS_LIST))).split(",")
most_common_empty_words_for_john = cltk_normalize(",".join(most_common_empty_words_for_john)).split(",")
#TODO: remove any greek words without accents
junk_words = set(np.concatenate((swadesh_words, stop_words, most_common_empty_words_for_john)))
clean_tokens = [word for word in lemmat if word not in junk_words] #len(clean_tokens) # 2,053,230 words -- much better!

#5. Serialize and write lemmata to disk
clean_lemmata_path = "/Users/paul/cltk_data/greek/text/real_chrysostom_corpus/ALL_REAL_JOHN_CLEAN_LEMMAS.TXT"
serializable_lemmas = '|'.join(clean_tokens)
file = open(clean_lemmata_path, 'w')
file.write(serializable_lemmas)
file.close()
len(clean_tokens)
##### WTF?!?!###
## Dude -- move everything to betacode with no accents. Done. Fuck this shit. Python SUCKS at Greek. Buggy as hell. Equals is broken. Maybe CLTK normalize is broken. I don't know and I dont care. I am FUCKING DONE!
## assert "πᾶς" not in clean_tokens[20:80] # I copied it out of the fucking output!!
###
# TODO: FIX TLG corpus importer so you can train new word2vec models if these ones suck
# the problem was it was globing the files wrong and picking up the .Trashes file. Should
# be a 1 line fix to have it ignore dot files.

############# Preprocssing Complete #############
