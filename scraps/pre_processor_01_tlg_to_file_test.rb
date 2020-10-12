require "fileutils"
require "rgreek"
require "set"
include RGreek

SAMPLE = <<~THERE
  Εἰ καὶ δάκρυα καὶ στεναγμοὺς ἦν διὰ γραμμάτων δηλοῦσθαι,
  καὶ τούτων ἄν σοι τὴν ἐπιστολὴν ἐμπλήσας ἀπέστειλα·
  δακρύω δὲ ἐγὼ οὐχ ὅτι πραγμάτων φροντίζεις πατρῴων, ἀλλ'
  ὅτι τοῦ καταλόγου τῶν ἀδελφῶν σαυτὸν ἐξήλειψας, ὅτι τὰς
  πρὸς τὸν Χριστὸν συνθήκας κατεπάτησας. Ταῦτα φρίττω,
  ἐπὶ τούτοις ἀλγῶ, διὰ τοῦτο φοβοῦμαι καὶ τρέμω, &lt;καὶ οὐκ
  ἀδίκως&gt;. Ἰδιώτην μὲν γὰρ οὐδεὶς λειποστρατίας ἄν ποτε
  γράψαιτο, ὁ δὲ στρατιώτης ἅπαξ γενόμενος ἐὰν ἁλῷ λιποτακτήσας
  περὶ τῶν ἐσχάτων ὁ κίνδυνος· Οὐ δεινόν, ὦ φίλε
  Θεόδωρε, τὸ παλαίοντα πεσεῖν ἀλλὰ τὸ μεῖναι ἐν τῷ πτώματι·
  οὐδὲ χαλεπὸν τὸ πολεμοῦντα τρωθῆναι, ἀλλὰ τὸ μετὰ τὴν <pb/>
  πληγὴν ἀπογνόντα καταμελῆσαι τοῦ τραύματος. Οὐδεὶς ἔμπορος
  ἅπαξ ναυαγίῳ περιπεσὼν καὶ τὸν φόρτον ἀπολέσας,
  ἀπέστη τοῦ πλεῖν, ἀλλὰ πάλιν τὴν θάλασσαν καὶ τὰ κύματα
  καὶ τὰ μακρὰ διαπερᾷ πελάγη καὶ τὸν πρότερον ἀνακτᾶται
  πλοῦτον. Πολλάκις καὶ ἀθλητὰς θεωροῦμεν μετὰ πολλὰ πτώματα
  στεφανίτας γινομένους· ἤδη δὲ καὶ στρατιώτης πολλάκις
  φυγὼν ἔσχατον ἀριστεὺς ἀπεδείχθη, καὶ τῶν πολεμίων ἐπεκράτησεν.
  Πολλοὶ δὲ καὶ τῶν τὸν Χριστὸν ἀρνησαμένων διὰ τὴν
  τῶν βασάνων ἀνάγκην ἀνεμαχέσαντο τὴν ἧτταν πάλιν καὶ τὸν
  τοῦ μαρτυρίου στέφανον ἀπῆλθον ἀναδησάμενοι. Εἰ δὲ τούτων
  ἕκαστος ἐκ τῆς προτέρας πληγῆς ἀπέγνω, οὐκ ἂν τῶν δευτέρων
  ἀπήλαυσεν ἀγαθῶν.
THERE

GREEK_PUNCTUATION = [",", ".", "·", ";", "'", " ","\n"]
UNICODE_GREEK = Set.new(RGreek::Transcoder::UNICODES.values + GREEK_PUNCTUATION)

def normalize_accents(text)
  RGreek::Transcoder.tonos_to_oxia(text)
end

def strip_non_greek(text)
  normalize_accents(text).split("").map { |char| char if UNICODE_GREEK.member?(char) }.join
end

def new_convert_to_betacode(text)
  text = strip_non_greek(text)
  #puts text.split("").map { |c| c unless RGreek::Transcoder.is_unicode?(c) }
end
semicolon = "\u037E"
puts semicolon == ";"
#puts new_convert_to_betacode(SAMPLE)
# puts new_convert_to_betacode(SAMPLE)

# Notes:
# 1. Results of preprocssing_pipeline.py are saved in /Users/paul/cltk_data/greek/text/real_chrysostom_corpus/ALL_REAL_JOHN_CLEAN_LEMMAS.TXT
# 2. The file is serialized using a | as a delimiter between words bc you explictily remove every | with the "english_text" regexp -- KEEP THAT.

BASE_PATH = "/Users/paul/cltk_data/greek/text/real_chrysostom_corpus/"
OUT_BASENAME = "ALL_REAL_JOHN_FOR_BAG_OF_WORDS.TXT"
PREPROCESSSED_BASENAME = "ALL_REAL_JOHN_CLEAN_LEMMAS.TXT"
PREPROCESSED_FILEPATH = BASE_PATH + PREPROCESSSED_BASENAME
OUT_FILE = BASE_PATH + OUT_BASENAME

BETACODE_DIACRITIALS = /[\(\)\/\\\|\=]/
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
#prep_john_for_bag_of_words
