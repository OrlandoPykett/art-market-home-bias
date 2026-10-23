# ------
# Numeric codes to country
# ------

COUNTRY_CODE_MAP = {
    1: "United States",    # Unverified
    2: "United Kingdom",    # Unverified
    3: "China",    # Unverified

    4: "Switzerland",
    5: "France",
    6: "Italy",
    7: "Sweden",
    8: "Germany",
    9: "Denmark",
    10: "Japan",
    11: "Taiwan",

    12: "Indonesia",             # Unverified

    13: "Norway",
    14: "Morocco",
    15: "Australia",
    16: "South Korea",
    17: "Austria",

    18: "Netherlands",             # Unverified

    19: "Brazil",
    20: "South Africa",

    21: "Iran",             # Unverified
    22: "Mexico",             # Unverified
    23: "Indonesia",             # Unverified

    24: "Argentina",
    25: "India"    
}

# ------
# City to country
# ------

CITY_COUNTRY_MAP = {

    """
    Notes

    "Arcade" used as place name in auctions by Sotheby's in various locations
    "Paris &amp; Jerusalem" joint sale between France and Israel, exact location unknown

    Unknown place names:
    "Avon"
    "East"

    """

    "nan": None,

    # Argentina
    "Buenos Aires": "Argentina",

    # Australia
    "Melbourne": "Australia",
    "South Yarra": "Australia",
    "South Yarra - Melbourne": "Australia",
    "Sydney": "Australia",
    
    # Austria
    "Graz": "Austria",
    "Vienna": "Austria",
    
    # Belgium
    "Antwerp": "Belgium",
    "Antwerp-Berchem": "Belgium",
    "Brussells": "Belgium",
    "Brussels": "Belgium",
    "Lokeren": "Belgium",

    # Brazil
    "Rio": "Brazil",
    "Rio de Janeiro": "Brazil",
    "Sao Paulo": "Brazil",
    "São Paulo": "Brazil",

    # Canada
    "Calgary": "Canada",
    "Toronto": "Canada",
    "Vancouver": "Canada",

    # China
    "Beijing": "China",
    "Hong Kong": "Hong Kong",
    "Shanghai": "China",

    # Colombia

    # Denmark
    "Bredgade": "Denmark",
    "Copenhagen": "Denmark",

    # Finland
    "Helsinki": "Finland",

    # France
    "Brest": "France",
    "Cannes": "France",
    "Deauville": "France",
    "Deurbergue &amp; Hoebanx": "France", # French auction house: Deurbergue & Hoebanx
    "Fontainebleau": "France",
    "L&#039;Isle-Adam": "France",
    "La Varenne-Saint-Hilaire": "France",
    "Lot 107 A - Libert/Briest/Jutheau": "France",
    "Lot 58 - Labat & Thierry": "France",
    "Lot 65 - Libert/Briest/Jutheau": "France",
    "Lyon Cedex 06": "France",
    "Marseille": "France",
    "Neuilly": "France",
    "Paris": "France",
    "Paris - Drouot": "France",
    "Paris Cedex 04": "France",
    "Provence-Côte d&#039;Azur": "France",
    "Rennes": "France",
    "Vannes": "France",
    "Versailles": "France",

    # Germany
    "Ahlden": "Germany",
    "Berlin": "Germany",
    "Berlin-Charlottenburg": "Germany",
    "Berlin-Grunewald": "Germany",
    "Bielefeld": "Germany",
    "Bremen": "Germany",
    "Cologne": "Germany",
    "Duesseldorf": "Germany",
    "Dusseldorf": "Germany",
    "Essen-Ruetenscheid": "Germany",
    "Frankfurt": "Germany",
    "Hamburg": "Germany",
    "Heidelberg": "Germany",
    "Heilbronn": "Germany",
    "Koenigstein im Taunus": "Germany",
    "Lindau": "Germany",
    "Munich": "Germany",
    "Saarbrucken/Scheidt": "Germany",
    "Staufen": "Germany",
    "Stuttgart": "Germany",

    # Greece
    "Athens": "Greece",
    
    # India
    "Mumbai": "India",

    # Indonesia
    "Jakarta": "Indonesia",

    # Ireland
    "Cork": "Ireland",
    "Dublin": "Ireland",

    # Israel
    "Hertzelia Pituch": "Israel",
    "Tel Aviv": "Israel",

    # Italy
    "Brescia": "Italy",
    "Florence": "Italy",
    "Genoa": "Italy",
    "Milan": "Italy",
    "Naples": "Italy",
    "Prato": "Italy",
    "Rome": "Italy",
    "Torino": "Italy",
    "Trieste": "Italy",
    "Turin": "Italy",
    "Venice": "Italy",
    "Vercelli": "Italy",    

    # Japan
    "Tokyo": "Japan",

    # Morocco
    "Casablanca": "Morocco",

    # Netherlands
    "Amsterdam": "Netherlands",
    "Lot 195 - Arts & Antiques Group": "Netherlands",
    "Lot 278 - Arts & Antiques Group": "Netherlands",
    "Lot 347 - Arts & Antiques Group": "Netherlands",
    "Lot 80 - Arts & Antiques Group": "Netherlands",
    "Lot 85 - Arts & Antiques Group": "Netherlands",

    # New Zealand
    "Auckland": "New Zealand",
    "Aukland": "New Zealand",

    # Norway
    "Oslo": "Norway",

    # Portugal
    "Lisbon": "Portugal",

    # Qatar
    "Doha": "Qatar",

    # Singapore
    "Singapore": "Singapore",

    # South Africa
    "Cape Town": "South Africa",
    "Johannesburg": "South Africa",
    
    # South Korea
    "Seoul": "South Korea",

    # Spain
    "Madrid": "Spain",

    # Sweden
    "Lund": "Sweden",
    "Stockholm": "Sweden",
    "Uppsala": "Sweden",
    
    # Switzerland
    "Bern": "Switzerland",
    "Geneva": "Switzerland",
    "Geneve": "Switzerland",
    "Lucerne": "Switzerland",
    "St. Gallen": "Switzerland",
    "Zurich": "Switzerland",
    

    # Taiwan
    "Taipei": "Taiwan",
    "Taiwan": "Taiwan",

    # United Arab Emirates
    "Dubai": "United Arab Emirates",

    # United States
    "Alameda": "United States",
    "Asheville": "United States",
    "Beverly": "United States", # unconfident
    "Boston": "United States",
    "Chevy Chase": "United States", # okay?
    "Chicago": "United States",
    "Cincinnati": "United States",
    "Cleveland": "United States",
    "Coral Gables": "United States",
    "Dallas": "United States",
    "Detroit": "United States",
    "Hudson": "United States", # Confidence: moderate
    "Lambertville": "United States",
    "Los Angeles": "United States",
    "Malvern": "United States",
    "Miami": "United States",
    "Milford": "United States",
    "NJ": "United States",
    "New Orleans": "United States",
    "New York": "United States",
    "Oakland": "United States",
    "Olympia": "United States",
    "Philadelphia": "United States",
    "S.F. &amp; L.A.": "United States",
    "S.F. & L.A.": "United States",
    "San Francisco": "United States",
    "Sherman Oaks": "United States",
    "St. Louis": "United States",
    "Van Nuys": "United States",
    "Washington": "United States",

    # United Kingdom
    "Alnwick": "United Kingdom",
    "Chelsea": "United Kingdom",
    "Edinburgh": "United Kingdom",
    "Haslemere": "United Kingdom",
    "Kensington": "United Kingdom",
    "Knightsbridge": "United Kingdom",
    "Knowle": "United Kingdom",
    "Leyburn": "United Kingdom",
    "London": "United Kingdom",
    "Marlborough": "United Kingdom",
    "Newbury": "United Kingdom",
    "Salisbury": "United Kingdom",
    "Shrewsbury": "United Kingdom",
    "South Cerney": "United Kingdom",
    "South Kensington": "United Kingdom",
    "Stansted Mountfitchet": "United Kingdom",
    "Wokin": "United Kingdom",

    # Venezuela
    "Caracas": "Venezuela"
 
}

# ------
# Nationality to country
# ------

NATIONALITY_COUNTRY_MAP = {
    "American": "United States",
    "German": "Germany",
    "British": "United Kingdom",
    "Italian": "Italy",
    "Austrian": "Austria",
    "Japanese": "Japan",
    "French": "France",
    "Swiss": "Switzerland",
    "Belgian": "Belgium",
    "Brazilian": "Brazil",
    "Icelandic": "Iceland",
    "Colombian": "Colombia",
    "Spanish": "Spain",
    "Chinese": "China",
    "South African": "South Africa",
    "Danish": "Denmark",
    "Dutch": "Netherlands",
    "Argentine": "Argentina",
    "Iranian": "Iran",
    "Canadian": "Canada",
    "Greek": "Greece",
    "Indian": "India",
    "Polish": "Poland",
    "Venezuelan": "Venezuela",
    "Mexican": "Mexico",
    "Portuguese": "Portugal",
    "Czech": "Czech Republic",
    "Korean": "South Korea",
    "Norwegian": "Norway",
    "Israeli": "Israel",
    "Australian": "Australia",
    "Egyptian": "Egypt",
    "Russian": "Russia",
    "Palestinian": "Palestine",
    "Chilean": "Chile",
    "Irish": "Ireland",
    "Malian": "Mali",
    "Pakistani": "Pakistan",
    "Ghanaian": "Ghana",
    "Scottish": "United Kingdom",
    "Algerian": "Algeria",
    "Cuban": "Cuba",
    "Cameroonian": "Cameroon",
    "Georgian": "Georgia",
    "Bulgarian": "Bulgaria",
    "Moroccan": "Morocco",
    "Finnish": "Finland",
    "Swedish": "Sweden",
    "Yugoslav": "Yugoslavia",
}

COUNTRIES = {
    "Algeria",
    "Argentina",
    "Australia",
    "Austria",
    "Belgium",
    "Brazil",
    "Bulgaria",
    "Cameroon",
    "Canada",
    "Chile",
    "China",
    "Colombia",
    "Cuba",
    "Czech Republic",
    "Denmark",
    "Egypt",
    "Finland",
    "France",
    "Georgia",
    "Germany",
    "Ghana",
    "Greece",
    "Hong Kong",
    "Iceland",
    "India",
    "Iran",
    "Ireland",
    "Israel",
    "Italy",
    "Japan",
    "Lebanon",
    "Mali",
    "Mexico",
    "Morocco",
    "Netherlands",
    "Norway",
    "Pakistan",
    "Palestine",
    "Poland",
    "Portugal",
    "Russia",
    "South Africa",
    "South Korea",
    "Spain",
    "Sweden",
    "Switzerland",
    "Taiwan",
    "United Kingdom",
    "United States",
    "Venezuela",
    "Yugoslavia",
}

ARTIST_NATIONALITY_MAP = {
    "BONNARDPIERRE": "France",
    "BOUDINEUGENE": "France",
    "BRAUNERVICTOR": "Romania",
    "CARRIEREEUGENE": "France",
    "CEZANNEPAUL": "France",
    "CHAGALLMARC": "Russia",
    "COROTJEANBAPT": "France",
    "DALISALVADOR": "Spain",
    "DEGASEDGAR": "France",
    "DELVAUXPAUL": "Belgium",
    "DERAINANDRE": "France",
    "DUFYJEAN": "France",
    "DUFYRAOUL": "France",
    "ENSORJAMES": "Belgium",
    "ERNSTMAX": "Germany",
    "ERTEROMANDET": "Romania",
    "ERTEROMADET": "Romania",
    "FORAINJEANLOU": "France",
    "FOUJITATSUGHOU": "Japan",
    "GAUGUINPAUL": "France",
    "GRISJUAN": "Spain",
    "GROSZGEORG": "Germany",
    "GUILLAMINJEAN": "France",
    "HELLEUPAULDES": "France",
    "KANDINSKYWASSI": "Russia",
    "KHNOPFFFERNAND": "Belgium",
    "KIRCHNERERNST": "Germany",
    "KISLINGMOISE": "Poland",
    "KLEEPAUL": "Switzerland",
    "KLIMTGUSTAV": "Austria",
    "KOKOSCHKAOSKAR": "Austria",
    "LAURENCINMARIE": "France",
    "LAURENSHENRI": "France",
    "LEGERFERNAND": "France",
    "LOISEAUGUSTAVE": "France",
    "MAGRITTERENE": "Belgium",
    "MANEKATZ": "France",
    "MANETEDOUARD": "France",
    "MATISSEHENRI": "France",
    "MIROJOAN": "Spain",
    "MODIGLIANIAMED": "Italy",
    "MONETCLAUDE": "France",
    "MORISOTBERTHE": "France",
    "MUNCHEDVARD": "Norway",
    "PICASSOPABLO": "Spain",
    "PISSARROCAMILL": "Denmark",
    "RENOIRPIERREA": "France",
    "ROUSSEAUHENRI": "France",
    "SEVERINIGINO": "Italy",
    "SIGNACPAUL": "France",
    "SISLEYALFRED": "United Kingdom",
    "TOULOUSELAUTREC": "France",
    "UTRILLOMAURICE": "France",
    "VALTATLOUIS": "France",
    "VANDONGENKEES": "Netherlands",
    "VANGOGHVINCEN": "Netherlands",
    "VANRYSSELBERGHE": "Belgium",
    "VLAMINCKMAURIC": "France",
    "VUILLARDEDOUAR": "France",
}

NATIONALITIES = {
    "American",
    "German",
    "British",
    "Italian",
    "Austrian",
    "Japanese",
    "French",
    "Swiss",
    "Belgian",
    "Brazilian",
    "Icelandic",
    "Colombian",
    "Spanish",
    "Chinese",
    "South African",
    "Danish",
    "Dutch",
    "Argentine",
    "Iranian",
    "Canadian",
    "Greek",
    "Indian",
    "Polish",
    "Venezuelan",
    "Mexican",
    "Portuguese",
    "Czech",
    "Korean",
    "Norwegian",
    "Israeli",
    "Australian",
    "Egyptian",
    "Russian",
    "Palestinian",
    "Chilean",
    "Irish",
    "Malian",
    "Pakistani",
    "Ghanaian",
    "Scottish",
    "Algerian",
    "Cuban",
    "Cameroonian",
    "Georgian",
    "Bulgarian",
    "Moroccan",
    "Finnish",
    "Swedish",
    "Yugoslav",
}

COUNTRY_ABBREVIATION_MAP = {
    "LO": "United Kingdom",
    "NY": "United States",
}

CEPII_COUNTRY_MAP = {
    "United States of America": "United States",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "Belgium and Luxembourg": "Belgium", # TODO handle country grouping
    "Russian Federation": "Russia",
    "Iran (Islamic Republic of)": "Iran",
    "Venezuela (Bolivarian Republic of)": "Venezuela",
    "China, Hong Kong Special Administrative Region": "Hong Kong",
    "Republic of Korea": "South Korea"
}


def convert_country(value):
    """
    Convert a value from the raw `country` column into a country name.

    Handles:
    * Numeric country codes
    * Existing country names
    * City/location names
    * Nationalities
    * Unknown values
    """

    if value is None:
        return None

    value = str(value).strip()

    # Missing values
    if value in {"", "nan", "None", "NaN", "N/A", "unknown"}:
        return None

    
    try:
        # Numeric country codes -> country
        code = int(float(value))

        if code in COUNTRY_CODE_MAP:
            return COUNTRY_CODE_MAP[code]
        
    except ValueError:
        pass

    # Already a country name
    if value in COUNTRIES:
        return value

    # Nationality -> country
    if value in NATIONALITY_COUNTRY_MAP:
        return NATIONALITY_COUNTRY_MAP.get(value)

    # Abbreviation -> country
    if value in COUNTRY_ABBREVIATION_MAP:
        return COUNTRY_ABBREVIATION_MAP.get(value)
    
    # CEPII format -> country
    if value in CEPII_COUNTRY_MAP:
        return CEPII_COUNTRY_MAP.get(value)

    # City/location → country
    if value in CITY_COUNTRY_MAP:
        return CITY_COUNTRY_MAP.get(value)


def map_sale_country(df):
    """
    Add a standardized `sale_country` column without
    modifying the original `country` column.
    """

    df["sale_country"] = df["country"].apply(convert_country)

    return df