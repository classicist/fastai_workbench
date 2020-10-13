JUNK_WORDS = [ 'ὁ', 'καὶ', 'οὗτος', 'τὴν', 'οὐ', 'γὰρ', 'εἰμί', 'τὸ', 'δὲ', 'αὐτός', 'τὸν', 'ἐγώ', 'τὰ', 'ἐν', 'ὅστις', 'μὴ', 'ἀλλὰ', 'σύ', 'λέγω1', 'πᾶς', 'ἀλλ', 'εἰς', 'τίς', 'διὰ', 'μὲν', 'γίγνομαι', 'εἰ', 'τοὺς', 'πρὸς', 'οὕτως', 'ποιέω', 'ἔχω', 'ἐκεῖνος', 'εἶπον', 'ἐπὶ', 'οὐδὲ', 'ἂν', 'τις', 'ἵνα', 'μετὰ', 'ὡς', 'ἀπὸ', 'οὖν', 'αὐτὸν', 'μόνος', 'ἐκ', 'περὶ', 'ὁράω', 'φημί', 'πολύς', 'πως', 'μέγας', 'τὰς', 'πάλιν','ἕτερος', 'ἢ', 'ὅταν', 'οὐδὲν', 'ἀκούω', 'εἶδον', 'τοσοῦτος', 'ἅπας', 'τοιοῦτος', 'ἐπειδὴ', 'δέω1', 'ἑαυτοῦ', 'δείκνυμι', 'κἂν', 'αὐτοὺς', 'ἐνταῦθα', 'μᾶλλον', 'κατὰ', 'οἶδα', 'φησὶν', 'ἄλλος', 'δοκέω', 'λόγος', 'ὑπὲρ', 'παρὰ', 'νῦν', 'τότε', 'κύριος', 'δίδωμι', 'ὥστε', 'ὅς', 'φησὶ', 'λαμβάνω', 'τοίνυν', 'πρότερος', 'μέλλω', 'πρᾶγμα', 'αὐτὸς', 'δι', 'γαῖα', 'ὥσπερ', 'ἥμερος', 'παῦλος', 'καλέω', 'ἐρῶ', 'σῶμα', 'παρ', 'δὴ', 'ὅσος', 'οὔτε', 'καθά', 'μηδὲ', 'γάρ', 'αὐτὸ', 'αὐτὴν', 'τε', 'ἔρχομαι', 'νόμος', 'σὺ', 'ὑπὸ', 'φέρω', 'ῥῆμα', 'ἵστημι', 'ἐὰν', 'οἰκέω', 'ὅσπερ', 'ἐργάζομαι', 'ὃ', 'λοιπὸν', 'νομίζω', 'ἐκεῖ', 'ἐγὼ', 'ἐπιδείκνυμι', 'ἅγιος', 'ἁπλόω', 'εἶτα', 'ἕκαστος', 'πάρειμι1', 'ἐπάγω', 'μάλιστα', 'οὐχὶ', 'εἷς', 'ἡμέτερος', 'οὐρανός', 'διὸ', 'καθ', 'πρὸ',              'ἕνεκα', 'ὅστε', 'δέ', 'πολλάκις', 'πολλὴν', 'τίθημι', 'ἐντεῦθεν', '<', '>', 'αἰών', 'ἵημι', 'ποτέ', 'ἐπεὶ', 'ἐναντίος', 'ἑαυτὸν', 'διαλέγω', 'μηδὲν', 'καίτοι', 'γε', 'ποῖος', 'ἄγω', 'τοῦτό', 'μυρίος', 'πανταχοῦ', 'δηλόω', 'ἐννοέω', 'οὐδείς', 'αὐτὰ', 'ἀεὶ', 'ἀνά', 'πολλὰ', 'πόσος', 'οὐδεὶς', 'γοῦν', 'εἰπὼν', 'ἔτι', 'πλείων', 'ἐστὶ', 'τυγχάνω', 'οἷος', 'πόλις', 'εὐθύς', 'κελεύω', 'μετ', 'δῆλος', 'ἑαυτοὺς', 'ἐστὶν', 'μεθ', 'πράσσω', 'πολλοὶ', 'πού', 'ἀνίστημι', 'μακάριος', 'μικρὸν', 'ἐπ', 'μήτε', 'δύο', 'αὐτοὶ', 'ὅλοξ', 'ἀρκέω', 'δεικνὺς', 'μέχρι', 'ἠώς', 'κατ', 'ἃ', 'ἣν', 'ὃν', 'ὢν', 'ἰδοὺ', 'ἀντὶ', 'τουτέστιν', 'ἀλλήλων', 'ἄνω1', 'μή', 'ἐπιτυγχάνω', 'ἔσχατος', 'παντὸς','εἰσέρχομαι', 'αὐτός', 'ἐκεῖνος', 'ἐνταῦθα','τοιοῦτος', 'κενόω','οὖν','ποῖος','οὐδείς', 'οὐδαμός','ἐφ_','ἐφ','ὅθεν','πλὴν','πολὺ','τουτέστι','ὅπου','ὅπως','οὐκοῦν','ἅμα','μὴν','βʹ','αʹ','γʹ','αγιοισ', 'δευτεραν','αρχιεπισκοπου', 'αρχιεπισκοπου_κωνσταντινουπολεωσ', 'εισ', 'εισ_την', 'την','εν', 'εν_πατροσ', 'πατροσ','επιστολην', 'ημων', 'ημων_ιωαννου','ιωαννου','«',':', "'",';','!', ]