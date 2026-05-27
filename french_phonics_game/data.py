LEVELS = {
    1: {"name": "Starter chunks", "focus": "Basic vowels and high-value chunks."},
    2: {"name": "Common spelling tricks", "focus": "More vowels, oi, qu, and silent finals."},
    3: {"name": "Nasals and French-looking words", "focus": "Nasals, ç, gn, and common patterns."},
    4: {"name": "Harder French sounds", "focus": "French u, French r, final e, and ill/ille."},
}


def p(id, level, graphemes, sound, examples, note):
    return {"id": f"pattern:{id}", "level": level, "graphemes": graphemes, "sound": sound, "examples": examples, "note": note}


def w(id, level, french, sound, meaning, chunks, notes):
    return {"id": f"word:{id}", "level": level, "french": french, "sound": sound, "meaning": meaning, "chunks": chunks, "notes": notes}


PATTERNS = [
    p("a", 1, ["a", "à", "â"], "ah", ["chat", "papa", "là", "ça", "madame", "table"], "Usually an open ah sound."),
    p("e-acute", 1, ["é"], "ay", ["café", "été", "bébé", "école", "télé"], "Closed e, often like ay."),
    p("i", 1, ["i", "î", "ï", "y"], "ee", ["ici", "il", "si", "île", "maïs", "style"], "Usually like English ee."),
    p("ou", 1, ["ou"], "oo", ["rouge", "vous", "nous", "jour", "bonjour", "où"], "Like English oo, not ow."),
    p("ch", 1, ["ch"], "sh", ["chat", "chocolat", "chaud", "chien", "chercher"], "Like English sh."),
    p("j-ge", 1, ["j", "ge"], "zh", ["je", "jour", "bonjour", "rouge", "manger", "gentil"], "Like the middle sound in measure."),
    p("e-open", 2, ["è", "ê", "ai", "ei"], "eh", ["mère", "père", "fête", "mais", "lait", "neige"], "More open than é."),
    p("er-ez", 2, ["er", "ez"], "ay", ["parler", "aimer", "manger", "nez", "vous avez"], "Final -er and -ez often sound like é."),
    p("o", 2, ["o", "ô"], "oh", ["mot", "dos", "trop", "hôtel", "côte"], "Often like oh."),
    p("au-eau", 2, ["au", "eau"], "oh", ["chaud", "eau", "beau", "gâteau", "bateau", "aussi"], "A common spelling for oh."),
    p("oi", 2, ["oi"], "wah", ["moi", "toi", "trois", "soir", "voilà", "boire"], "Often sounds like wah."),
    p("qu", 2, ["qu"], "k", ["quatre", "qui", "que", "quoi", "quand"], "Usually k, not English kw."),
    p("final-consonant", 2, ["final consonant"], "often silent", ["chat", "grand", "petit", "vous", "trop", "blanc"], "Final t, d, s, x, p, g are often silent."),
    p("an-en", 3, ["an", "am", "en", "em"], "nasal ahn", ["sans", "enfant", "temps", "jambe", "grand", "français"], "Nasal vowel; do not pronounce a full n/m."),
    p("on-om", 3, ["on", "om"], "nasal ohn", ["bonjour", "nom", "tomber", "garçon", "mon", "son"], "Nasal vowel; do not pronounce a full n/m."),
    p("in-ain-ein", 3, ["in", "im", "ain", "aim", "ein"], "nasal ehn", ["pain", "vin", "important", "plein", "main", "faim"], "Roughly ehn, but nasal."),
    p("un-um", 3, ["un", "um"], "nasal uhn", ["un", "brun", "lundi", "parfum"], "Often merges with nasal in in modern accents."),
    p("cedille", 3, ["ç"], "s", ["français", "garçon", "ça", "leçon", "façon", "reçu"], "Ç makes c sound like s before a, o, or u."),
    p("gn", 3, ["gn"], "ny", ["montagne", "champignon", "gagner", "ligne", "Espagne"], "Like ny in canyon."),
    p("s-ss", 3, ["s", "ss"], "s", ["salut", "poisson", "dessert", "aussi", "classe"], "Single s between vowels may sound like z; ss stays s."),
    p("u", 4, ["u", "û"], "French u", ["tu", "rue", "lune", "salut", "plus", "musique"], "Say ee while rounding your lips; not oo."),
    p("r", 4, ["r"], "back-of-throat r", ["rouge", "merci", "Paris", "très", "rue", "français"], "Light voiced friction in the back of the mouth."),
    p("final-e", 4, ["final e"], "usually weak/silent", ["rouge", "porte", "petite", "table", "fille"], "Often weak or silent, but it can make the previous consonant heard."),
    p("ill-ille", 4, ["ill", "ille"], "often y", ["fille", "famille", "travail", "soleil", "bouteille"], "Often a y-glide, with exceptions."),
]

WORDS = [
    w("chat", 1, "chat", "shah", "cat", ["ch", "a", "t"], ["ch = sh", "final t is silent"]),
    w("cafe", 1, "café", "kah-fay", "coffee / café", ["ca", "fé"], ["é = ay"]),
    w("je", 1, "je", "zhuh", "I", ["j", "e"], ["j = zh"]),
    w("vous", 1, "vous", "voo", "you, formal or plural", ["v", "ou", "s"], ["ou = oo", "final s is silent"]),
    w("nous", 1, "nous", "noo", "we / us", ["n", "ou", "s"], ["ou = oo", "final s is silent"]),
    w("jour", 1, "jour", "zhoor", "day", ["j", "ou", "r"], ["j = zh", "ou = oo", "final r is pronounced here"]),
    w("ou-accent", 1, "où", "oo", "where", ["où"], ["où sounds like ou; accent distinguishes it from ou = or"]),
    w("moi", 2, "moi", "mwah", "me", ["m", "oi"], ["oi = wah"]),
    w("toi", 2, "toi", "twah", "you / yourself", ["t", "oi"], ["oi = wah"]),
    w("eau", 2, "eau", "oh", "water", ["eau"], ["eau = oh"]),
    w("chaud", 2, "chaud", "shoh", "hot", ["ch", "aud"], ["ch = sh", "au = oh", "final d is silent"]),
    w("beau", 2, "beau", "boh", "beautiful / handsome", ["b", "eau"], ["eau = oh"]),
    w("petit", 2, "petit", "puh-tee", "small", ["pe", "ti", "t"], ["final t is usually silent"]),
    w("tres", 2, "très", "treh", "very", ["tr", "ès"], ["è = eh", "final s is silent"]),
    w("nez", 2, "nez", "nay", "nose", ["n", "ez"], ["final ez = ay"]),
    w("bonjour", 3, "bonjour", "bohn-zhoor", "hello / good morning", ["bon", "jour"], ["on = nasal ohn", "j = zh", "ou = oo"]),
    w("francais", 3, "français", "frahn-seh", "French", ["fr", "an", "ç", "ais"], ["an = nasal ahn", "ç = s", "ais often sounds like eh"]),
    w("pain", 3, "pain", "pehn", "bread", ["p", "ain"], ["ain = nasal ehn"]),
    w("garcon", 3, "garçon", "gahr-sohn", "boy / waiter", ["gar", "ç", "on"], ["ç = s", "on = nasal ohn"]),
    w("montagne", 3, "montagne", "mohn-tany", "mountain", ["mon", "ta", "gne"], ["on = nasal ohn", "gn = ny"]),
    w("grand", 3, "grand", "grahn", "big / tall", ["gr", "an", "d"], ["an = nasal ahn", "final d is silent"]),
    w("lecon", 3, "leçon", "luh-sohn", "lesson", ["le", "ç", "on"], ["ç = s", "on = nasal ohn"]),
    w("merci", 4, "merci", "mehr-see", "thank you", ["m", "er", "ci"], ["French r is light and in the back of the mouth"]),
    w("rouge", 4, "rouge", "ghoozh", "red", ["r", "ou", "ge"], ["r is back-of-throat", "ou = oo", "ge here sounds like zh"]),
    w("lune", 4, "lune", "French luun", "moon", ["l", "u", "ne"], ["u is the rounded French u, not oo"]),
    w("rue", 4, "rue", "French rü", "street", ["r", "u", "e"], ["r is back-of-throat", "u is rounded"]),
    w("fille", 4, "fille", "fee-yuh", "girl / daughter", ["fi", "lle"], ["ille often sounds like y after a vowel; fille is high-frequency"]),
    w("suis", 4, "suis", "swee", "am", ["s", "ui", "s"], ["ui is a glide; final s is silent"]),
    w("salut", 4, "salut", "sah-lü", "hi / bye", ["sa", "l", "u", "t"], ["u is rounded", "final t is silent"]),
    w("paris", 4, "Paris", "pah-ree", "Paris", ["Pa", "ri", "s"], ["final s is silent; French r is light/back"]),
]
