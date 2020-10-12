require "fileutils"
require "rgreek"
include RGreek

SAMPLE = "..56p.385*.22t  {Εἰς τὸ γενέθλιον τοῦ Σωτῆρος ἡμῶν Ἰησοῦ Χριστοῦ, Λόγος.}
..56p.385*.23t    Μυστήριον ξένον καὶ παράδοξον βλέπω: ποιμένες
..56p.385*.24t  μου περιηχοῦσι τὰ ὦτα, οὐκ ἔρημον (sic) συρίζοντες
..56p.385*.25t  μέλος, ἀλλ' οὐράνιον ᾄδοντες ὕμνον. Ἄγγελοι ᾄδου-
..56p.385*.26t  σιν, ἀρχάγγελοι μέλπουσιν, ὑμνεῖ τὰ Χερουβὶμ, δοξο-
..56p.385*.27t  λογεῖ τὰ Σεραφὶμ, πάντες ἑορτάζουσι Θεὸν ἐπὶ γῆς
..56p.385*.28t  ὁρῶντες, καὶ ἄνθρωπον ἐν οὐρανοῖς: τὸν ἄνω κάτω
..56p.385*.29t  δι' οἰκονομίαν, καὶ τὸν κάτω ἄνω διὰ φιλανθρωπίαν.
..56p.385*.30t  Σήμερον Βηθλεὲμ τὸν οὐρανὸν ἐμιμήσατο: ἀντὶ μὲν"

# Notes:
# 1. Results of preprocssing_pipeline.py are saved in /Users/paul/cltk_data/greek/text/real_chrysostom_corpus/ALL_REAL_JOHN_CLEAN_LEMMAS.TXT
# 2. The file is serialized using a | as a delimiter between words bc you explictily remove every | with the "english_text" regexp -- KEEP THAT.

BASE_PATH = "/Users/paul/cltk_data/greek/text/real_chrysostom_corpus/"
OUT_BASENAME = "ALL_REAL_JOHN_FOR_BAG_OF_WORDS.TXT"
PREPROCESSSED_BASENAME = "ALL_REAL_JOHN_CLEAN_LEMMAS.TXT"
PREPROCESSED_FILEPATH = BASE_PATH + PREPROCESSSED_BASENAME
OUT_FILE = BASE_PATH + OUT_BASENAME

BETACODE_DIACRITIALS = /[\(\)\/\\\|\=]/
TLG_LINE_NUMBERING = /^.*?\s+/
TLG_TITLES = /[{}]/
ENGLISH_TEXT = /[A-ZA-Z\[\]\)\(\\\=\+\|\*\#\%\+\@\~\`\$\^\&\\]/ # leave in Greek punctuation and elision marks: ',":·;.
NUMBERS = /0-9/
EXTRA_SPACES = /\s{2,4}/
LINES_ENDING_IN_HYPHENS = /-\n/
LINE_ENDINGS = /\n/

def prep_john_for_bag_of_words
  real_chrysostom_text = ""
  total_files = Dir["#{BASE_PATH}/*"].length
  start_time = Time.now
  Dir["#{BASE_PATH}/*"].sort.each_with_index do |filename, index|
    unless filename.include?(OUT_BASENAME) || filename.include?(PREPROCESSSED_BASENAME)
      text = File.open(filename, "r:UTF-8").read
      puts "converting #{filename}, #{index + 1} of #{total_files} (#{(index + 1) / total_files}% complete, #{(Time.now - start_time) / 60} minutes elapsed)"
      real_chrysostom_text << convert_to_betacode(cleanup_greek_text(text)) + "\n\n"
      break if TEST_MODE && index == 9
    end
  end
  write(real_chrysostom_text)
end

def cleanup_greek_text(text)
  # TODO: FIX: LINE-ENDINGS for some reason matches the space before an accented vowel near the end of a line
  text.gsub(TLG_LINE_NUMBERING, "").gsub(TLG_TITLES, "").gsub(ENGLISH_TEXT, "").gsub(NUMBERS, "").gsub(LINES_ENDING_IN_HYPHENS, "").gsub(LINE_ENDINGS, " ").downcase
end

def remove_diacritics_from_betacode(text)
  text.gsub(BETACODE_DIACRITIALS, "")
end

def convert_to_betacode(text)
  # NOTE: Betacode conversion wth rgreek is SLOW (+30m last time just to do John)
  # Commented out for speed while I fix the REGEXES
  # remove_diacritics_from_betacode RGreek::Transcoder.convert(text)
  text
end

def write(real_chrysostom_text)
  puts "WRITING FILE IN TEST MODE = #{TEST_MODE}"
  writer = TEST_MODE ? StringIO : File
  if TEST_MODE
    puts real_chrysostom_text[0..1000]
  else
    writer.open(OUT_FILE, "w") { |f| f.puts real_chrysostom_text }
  end
  puts "Wrote #{real_chrysostom_text.length} chars to #{OUT_FILE}"
end

TEST_MODE = true
prep_john_for_bag_of_words
