## Each Space is a cell in a juptyr notebook ("QuickThinking" in fastai_workbench) that runs on Gradient Paperspace
from greek_normalisation.utils import (nfd, nfc, convert_to_2019)
from greek_accentuation.characters import base
from cltk.lemmatize.grc import GreekBackoffLemmatizer
from alphabet import filter_non_greek, filter_non_greek_with_punctuation
from alphabet import PUNCTUATION
from cltk.stops.grc import STOPS
from greek_swadesh import SWADESH
from chrysostom_junk_words import JUNK_WORDS
import numpy as np
import datetime
from gensim.models import Phrases
from gensim.models import Word2Vec
from gensim.corpora import Dictionary

import sys
import pickle
import bz2


class TextDataSet:
    def __init__(self, file_path="default_text", verbose=True):
        self.file_path = file_path
        self.verbose = verbose
        self.mode_dataset_percentages = {
            'development': 0.05,
            'exploration': 0.25,
            'training': 0.70,
            'testing': 0.90,
            'validation': 1.0
        }

        if self.file_path != "default_text":
            file = open(file_path)
            self.text = file.read()
            file.close()
        else:
            self.text = 'ὁ αὐτὸς μῆνιν ἄειδε θεὰ Πηληϊάδεω Ἀχιλῆος; \nκαὶ κατέβην χθὲς εἰς Πειραιᾶ μετὰ Γλαύκωνος τοῦ Ἀρίστωνος. Τιμταμ;'
        # Defer: pass in a lambda to split into docs, if I need it
        self.all_documents = self.text.split('.')
        self.number_of_documents = len(self.all_documents)

        if self.verbose:
            print("segmented text into documents from: " + self.file_path)
            print("loaded " + str(self.number_of_documents) +
                  " total documents")

    def __texts_for_mode(self, current_mode, prior_mode):
        self.start_index = self.__start_index(prior_mode)
        self.end_index = self.__end_index(current_mode)
        documents = self.all_documents[self.start_index:self.end_index]
        greek_text = '.'.join(documents)
        if self.verbose:
            print("selected document range for: " + current_mode)
            print("selected " + str(len(documents)) +
                  " documents from indexes: " + str(self.start_index) + ':' +
                  str(self.end_index))
            print("percent selected for processeing: " +
                  str(self.mode_dataset_percentages[current_mode] * 100))
        return greek_text

    def __start_index(self, prior_mode):
        if prior_mode == None:
            start_index = 0
        else:
            prior_document_end_index = self.number_of_documents * \
                self.mode_dataset_percentages[prior_mode]
            start_index = prior_document_end_index + 1
        return int(start_index)

    def __end_index(self, current_mode):
        return int(self.number_of_documents *
                   self.mode_dataset_percentages[current_mode])

    def development(self):
        self.mode = sys._getframe().f_code.co_name
        return self.__texts_for_mode(self.mode, None)

    def exploration(self):
        self.mode = sys._getframe().f_code.co_name
        return self.__texts_for_mode(self.mode, None)

    def training(self):
        self.mode = sys._getframe().f_code.co_name
        return self.__texts_for_mode(self.mode, None)

    def testing(self):
        self.mode = sys._getframe().f_code.co_name
        return self.__texts_for_mode(self.mode, 'training')

    def validation(self):
        self.mode = sys._getframe().f_code.co_name
        return self.__texts_for_mode(self.mode, 'testing')


class GreekPreprocessor:
    def __init__(self, lemmatizer_class=GreekBackoffLemmatizer, verbose=True):
        self.build_unhelpful_word_list()
        self.lemmatizer = lemmatizer_class()
        self.verbose = verbose

    def build_unhelpful_word_list(self):
        stops = sorted(self.normalize_greek(' '.join(STOPS)).split(' '))
        swadesh = sorted(self.normalize_greek(' '.join(SWADESH)).split(' '))
        empty = ['', ' ', '\n']
        common = [
            'ἄνευ', 'εισ', 'ὡσανεὶ', 'θ', 'ταῦτ', 'πρό', 'δήποτε', 'δεύτερος',
            'αἰών', 'τοσοῦτος', 'ποτέ', 'ἴσως', 'ἐκεῖνος', 'ἐπεί', 'ἀνά',
            'εἴτε', 'φησὶ,', 'ἰδοὺ', 'εἶπε,', 'πῶς,', 'τοσοῦτον,', 'ὅσος',
            'μηδείς', 'μηδέ', 'μήν', 'γὰρ,', 'εἶπον', 'ἐστὶν,', 'ἐστὶν', 'ὅτε',
            'ποῖος', 'μοι,', 'ἐρῶ', 'τοῦτο,', 'ἀντί', 'πόσος', 'ἐστιν',
            'εἶπεν', 'εὐθύς', 'ποῦ', 'ἔμπροσθεν', 'ἀπαιτέω', 'κἀν', 'διό'
            'ποτέ'
            'ἵημι'
            'ἡμῶν,'
            'σαφής'
            'ὅπου', 'γίγνομαι', 'ἵημι', 'ἐντεῦθεν', 'ἕνεκα', 'σου', 'δοκέω',
            'φησὶ', 'φημί', 'τίθημι', 'γὰρ', 'τοσοῦτος', 'ὅσπερ', 'πᾶς',
            'μόνος', 'ὅταν', 'ἅπας', 'δύναμαι', 'καθά', 'τοσοῦτος', 'ἀρετή',
            'ἡμέτερος', 'ἀεί', 'τουτέστι,', 'πλῆθος', 'αὐτὸν', 'εἶναι', 'ἦν',
            'ἐστιν,'
            'ἐπειδὴ', 'αὐτῷ', 'αὐτοὺς', 'τότε', 'τούτου', 'πάντες', 'αὕτη',
            'ἦν', 'πάντας', 'ὅμως', 'φησιν', 'τουτέστι', 'ἔχειν', 'πλέον',
            'ἑαυτοὺς', 'οὕτω', 'οὐχ', 'ὥσπερ', 'ἐστι', 'ἐστιν', 'μόνον',
            'τοῦτό', 'ἔχει', 'ὑμᾶς', 'ἐστὶ', 'μέγα', 'γῆς', 'ποιεῖν',
            'τοσοῦτον', 'ὅσον', 'μικρὸν', 'γοῦν', 'γέγονε', 'ἵνα', 'ἡμᾶς',
            'ἡμῶν', 'σου', 'σε', 'εἶπεν', 'με', 'πᾶσαν', 'κατ', 'ἐκεῖνο',
            'εἶπεν', 'αὐτῇ', 'γένοιτο', 'καθάπερ', 'ἔστι', 'ἐστιν', 'ὑμῶν',
            'ἕτερον', 'οὗ', 'ἀεὶ', 'οἷς', 'λέγοντος', 'ἐμοὶ', 'νῦν', 'ταῦτα',
            'πάντα', 'μόνον', 'ἡμῖν', 'τούτων', 'πάντων', 'οὐχὶ', 'ἐκείνων',
            'μηδὲν', 'δὲ', 'τοῦτον', 'ἐστὶν', 'ἐκεῖνα', 'ἆρα', 'μετ', 'λέγων',
            'α', 'ἄλλως', 'οὐδὲν', 'φησὶ', 'πάλιν', 'αὐτοῖς', 'εἶτα', 'πολλὰ',
            'καλῶς', 'ἃ', 'τοιοῦτον', 'ἐκεῖνοι', 'εἶναι', 'χρὴ', 'μείζονα',
            'τουτέστιν', 'αὑτοῦ', 'πάντοθεν', 'αἰτίαν', 'τοῦτο', 'τὰς', 'αἱ',
            'μηδὲ', 'αὐτὴν', 'καίτοι', 'ἄλλων', 'ποιεῖ', 'γενέσθαι', 'ποτε',
            'εἶπε', 'παντὸς', 'ἐκείνην', 'οἷον', 'ἀλλὰ', 'ἕκαστος', 'εἰπεῖν',
            'φησὶν', 'δι', 'τοίνυν', 'ταύτην', 'πάλιν', 'ὧν', 'σφόδρα', 'σοι',
            'εὐθέως', 'δῆλον', 'πολλὴν', 'ἕως', 'πόθεν', 'ἤδη', 'οὖν', 'εἰσιν',
            'τὸ', 'οὐδέν', 'δεῖ', 'γὰρ', 'ὃ', 'λέγων', 'μου', 'τούτῳ', 'ἐπεὶ',
            'πρῶτον', 'λέγει', 'οὐκοῦν', 'αὐτοὶ', 'οὗτοι', 'γ', 'αὐτόν',
            'φησι', 'ταῖς', 'ὅπερ', 'ὁρᾷς', 'αὐτῆς', 'ὄντως', 'ἐκείνου',
            'μήτε', 'μοι', 'διὸ', 'χωρὶς', 'ἅμα', 'εἰπέ', 'εἰπέ_μοι', 'ἔσται',
            'ὁμοίως', 'ἐκείνῳ', 'αὐτοῦ', 'αὐτῶν', 'παρ', 'γίνεται', 'λέγω',
            'οὐκέτι', 'τοιαῦτα', 'εἰκότως', 'αὐτοῦ', 'ἑτέρων', 'β', 'ἐκείνης',
            'μὴν', 'πολλῆς', 'πολλάκις', 'ἁπλῶς', 'ἕνεκεν', 'αὐτὰ', 'ὑμῖν',
            'τίνος', 'πάσης', 'φησι', 'μυρία', 'τίνος_ἕνεκεν', 'ἔχων', 'ἧς',
            'νῦν', 'αὐτὸ', 'ἔστιν', 'φησίν', 'καθ', 'λέγει', 'μέχρι', 'πρὸ',
            'πᾶν', 'τοῦτο', 'ἐκεῖνον', 'ἅπερ', 'πολλοὶ', 'ἄλλο', 'ἦσαν',
            'ἔλεγεν', 'ἀμήν', 'μοι', 'μάλιστα', 'ταύτης', 'ἐστι', 'πανταχοῦ',
            'φησί', 'λοιπὸν', 'εἰπεῖν', 'τινες', 'πολὺ', 'ἐστίν', 'ἅπαντα',
            'ἀντὶ', 'οὐδαμοῦ', 'ἀλλήλους', 'μᾶλλον', 'κἂν', 'πολλῷ', 'εἴ',
            'πολλῷ', 'μᾶλλον', 'νόμον', 'ἔνθα', 'ᾖ', 'τούτοις', 'ταχέως',
            'εἶδες', 'ὅλως', 'οὐδέποτε'
        ]
        self.unhelpful_words = sorted(
            list(set(np.concatenate((stops, swadesh, empty, common)))))
        return self.unhelpful_words

    def strip_diacriticals(self, greek_text):
        return ''.join([base(char) for char in greek_text])

    def normalize_greek(self, greek_text):
        greek_text = nfc(
            greek_text
        )  # normalize pre-composed unicode characters to be single characters
        print("nfc-ed")
        greek_text = convert_to_2019(
            greek_text).lower()  # normalize apostrophes and lowercase
        print("converted_to_2019")

        # Run out of Memory here for with Training Mode data:
        greek_text = filter_non_greek_with_punctuation(
            greek_text)  # strip everything but greek and basic punctuation
        print("filtered_non_greek")
        greek_text = greek_text.replace(';', '.').replace(
            '·', '.')  # replace all punctuation except ","s with "."s
        print("replaced punctuation")
        return greek_text

    def remove_words_unhelpful_for_lda(self, lemmata):
        helpful_words = [
            word for word in lemmata
            if word not in self.unhelpful_words and word != '' and word != None
        ]
        return helpful_words

    def tokenize(self, sentence):
        sentence = sentence.replace(',', '').split(' ')
        lemmatized_tuples = self.lemmatizer.lemmatize(sentence)
        lemmata = [tuple[1] for tuple in lemmatized_tuples]
        lemmata = self.remove_words_unhelpful_for_lda(lemmata)
        return lemmata

    def make_lda_documents(self, greek_text):
        # LDA wants a List of Lists of words (= document), it will make each
        # sentence a document
        if self.verbose:
            print("chars in greek text:")
            print(len(greek_text))
            print("words in greek text:")
            print(len(greek_text.split(' ')))
            print("normalizing greek...")
            start_normalizing = datetime.datetime.now()
            print(start_normalizing)

        documents = self.normalize_greek(greek_text).split('.')

        if self.verbose:
            print("...done.")
            done_normalizing = datetime.datetime.now()
            print(done_normalizing)
            print("tokenizing...")
            start_tokenizing = datetime.datetime.now()
            print(start_tokenizing)

        lda_documents = []
        sentences_per_document = 50  # doc ~ a paragraph / thought
        current_document = []

        for sentence in documents:
            if len(sentence) > 0:
                sentence = self.tokenize(sentence)
            if len(sentence) > 0:
                current_document.extend(sentence)
                if len(current_document) >= sentences_per_document:
                    lda_documents.append(current_document)
                    current_document = []

        if self.verbose:
            print("...done.")
            done_tokenizing = datetime.datetime.now()
            print(done_tokenizing)
            print("number of lda_documents:")
            print(len(lda_documents))
            print("peek at lda_documents:")
            print(lda_documents[-3])

        return lda_documents

    def add_bigrams(self, documents, min_count=20):
        # Add bigrams and trigrams to docs (only ones that appear 20 times or
        # more).
        bigram = Phrases(documents, min_count=min_count)
        for idx in range(len(documents)):
            for token in bigram[documents[idx]]:
                if '_' in token:
                    # Token is a bigram, add to document.
                    documents[idx].append(token)
        return documents

    def make_dictionary(self, documents, no_below=20, no_above=0.5):
        # Remove rare and common tokens (Filter out words that occur less
        # than 20 documents, or more than 50% of the documents)

        dictionary = Dictionary(documents)
        dictionary.filter_extremes(no_below=no_below, no_above=no_below)
        return dictionary

    def make_bag_of_words_corpus(self, dictionary, documents):
        # Vectorize documents into Bag-of-words.
        bag_of_words_corpus = [dictionary.doc2bow(doc) for doc in documents]
        if self.verbose:
            # Let’s see how many tokens and documents we have to train on.
            print('Number of unique tokens: %d' % len(dictionary))
            print('Number of documents: %d' % len(bag_of_words_corpus))
        return bag_of_words_corpus

    def lda_corpus_factory(self, greek_text):
        lda_documents = self.make_lda_documents(greek_text)
        lda_documents = self.add_bigrams(lda_documents)
        dictionary = self.make_dictionary(lda_documents)
        corpus = self.make_bag_of_words_corpus(dictionary, lda_documents)
        return (corpus, dictionary, lda_documents)

    def word2vec_corpus_factory(self, greek_text):
        lda_documents = self.make_lda_documents(greek_text)
        lda_documents = self.add_bigrams(lda_documents)
        return lda_documents

    def serialize(self, lda_corpus, lda_documents, lda_dictionary,
                  word2vec_documents, mode_of_dataset):
        word2vec_documents_file = \
            bz2.BZ2File(f'{base_path}/{mode_of_dataset}_word2vec_documents_chrysostom.pickle', 'w')
        lda_documents_file = \
            bz2.BZ2File(f'{base_path}/{mode_of_dataset}_lda_documents_chrysostom.pickle', 'w')
        lda_dictionary_file = \
            bz2.BZ2File(f'{base_path}/{mode_of_dataset}_lda_dictionary_chrysostom.pickle', 'w')
        lda_corpus_file = \
            bz2.BZ2File(f'{base_path}/{mode_of_dataset}_lda_corpus_chrysostom.pickle', 'w')

        pickle.dump(word2vec_documents, word2vec_documents_file)
        pickle.dump(lda_documents, lda_documents_file)
        pickle.dump(lda_dictionary, lda_dictionary_file)
        pickle.dump(lda_corpus, lda_corpus_file)

        word2vec_documents_file.close()
        lda_documents_file.close()
        lda_dictionary_file.close()
        lda_corpus_file.close()

    def deserialize(self, mode_of_dataset):
        word2vec_documents_file = \
            bz2.BZ2File(f'{base_path}/{mode_of_dataset}_word2vec_documents_chrysostom.pickle', 'rb')
        lda_documents_file = \
            bz2.BZ2File(f'{base_path}/{mode_of_dataset}_lda_documents_chrysostom.pickle', 'rb')
        lda_dictionary_file = \
            bz2.BZ2File(f'{base_path}/{mode_of_dataset}_lda_dictionary_chrysostom.pickle', 'rb')
        lda_corpus_file = \
            bz2.BZ2File(f'{base_path}/{mode_of_dataset}_lda_corpus_chrysostom.pickle', 'rb')

        word2vec_documents = pickle.load(word2vec_documents_file)
        lda_documents = pickle.load(lda_documents_file)
        lda_dictionary = pickle.load(lda_dictionary_file)
        lda_corpus = pickle.load(lda_corpus_file)

        word2vec_documents_file.close()
        lda_documents_file.close()
        lda_dictionary_file.close()
        lda_corpus_file.close()

        return [word2vec_documents, lda_documents, lda_dictionary, lda_corpus]


base_path = '/Users/paul/dev/fastai_workbench'
path = f'{base_path}/ALL_REAL_JOHN_FOR_BAG_OF_WORDS.TXT'
mode_of_dataset = 'development'
greek_text = TextDataSet(path).development()  # select training data
preprocessor = GreekPreprocessor()

word2vec_documents = preprocessor.word2vec_corpus_factory(greek_text)
lda_corpus, lda_dictionary, lda_documents = \
    preprocessor.lda_corpus_factory(greek_text)

preprocessor.serialize(lda_corpus, lda_documents, lda_dictionary,
                       word2vec_documents, mode_of_dataset)
# word2vec_documents, lda_documents, lda_dictionary, lda_corpus = \
# preprocessor.deserialize(mode_of_dataset)
