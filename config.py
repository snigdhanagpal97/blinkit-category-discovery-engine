"""Central config for the discovery engine (Blinkit primary + competitor benchmark)."""

# --- Blinkit (primary) app IDs (verified July 2026) ---
PLAYSTORE_APP_ID = "com.grofers.customerapp"
APPSTORE_APP_ID = "960335206"

REVIEW_LANG = "en"
REVIEW_COUNTRY = "in"
PLAYSTORE_TARGET = 1500
APPSTORE_MAX_PAGES = 10

# --- Competitors for the cross-platform benchmark (verified July 2026) ---
COMPETITORS = {
    "zepto":     {"playstore": "com.zeptoconsumerapp",   "appstore": "1575323645"},
    "bigbasket": {"playstore": "com.bigbasket.mobileapp", "appstore": "660683603"},
}
COMPETITOR_PLAYSTORE_TARGET = 800     # per competitor
COMPETITOR_APPSTORE_MAX_PAGES = 8     # per competitor (~400 each)

# --- Reddit ---
REDDIT_SUBREDDITS = [
    "india", "bangalore", "mumbai", "delhi", "pune", "hyderabad",
    "IndianStreetBets", "developersIndia", "IndiaInvestments",
]
REDDIT_QUERIES = [

    # KNOW — awareness of assortment breadth
    '"didn\'t know" Blinkit',
    '"did not know" Blinkit',
    '"Blinkit sells"',
    '"found on Blinkit"',
    '"discovered on Blinkit"',
    '"surprised" Blinkit',
    '"things you buy" Blinkit',
    '"what do you buy" Blinkit',

    # CONSIDER — mental availability / platform choice
    '"Blinkit or Amazon"',
    '"Amazon vs Blinkit"',
    '"Blinkit vs Amazon"',
    '"Blinkit vs Nykaa"',
    '"Blinkit vs Flipkart"',
    '"buy electronics" Blinkit',
    '"buy clothes" Blinkit',
    '"buy skincare" Blinkit',

    # CONFIDENCE — higher-consideration purchases
    '"Blinkit electronics" genuine',
    '"Blinkit beauty" original',
    '"Blinkit skincare" genuine',
    '"Blinkit warranty"',
    '"Blinkit authenticity"',
    '"Blinkit expensive product"',
    '"Blinkit returns" electronics',

    # HABIT
    '"always order" Blinkit',
    '"only use" Blinkit',
    '"use Blinkit for groceries"',
    '"same things" Blinkit',
    '"everyday" Blinkit',
    '"daily" Blinkit',
    '"Blinkit routine"',
    '"addicted to Blinkit"',

    # CONTEXT / TRIGGERS
    '"Blinkit pet"',
    '"Blinkit baby"',
    '"Blinkit party"',
    '"Blinkit emergency"',
    '"Blinkit last minute"',
    '"Blinkit birthday"',
    '"Blinkit festival"',
    '"needed urgently" Blinkit',
]
REDDIT_POST_LIMIT = 60
REDDIT_COMMENTS_PER_POST = 15

# --- YouTube (each query tagged with the platform it's about) ---
YOUTUBE_QUERIES = [
    # General Blinkit behavior
    ("Blinkit review", "blinkit"),
    ("Blinkit shopping haul", "blinkit"),
    ("Blinkit new categories", "blinkit"),

    # Unexpected assortment / awareness
    ("things you didn't know Blinkit sells", "blinkit"),
    ("unexpected things on Blinkit", "blinkit"),

    # Higher-consideration categories
    ("Blinkit electronics review", "blinkit"),
    ("ordering electronics from Blinkit", "blinkit"),
    ("Blinkit beauty haul", "blinkit"),
    ("Blinkit fashion haul", "blinkit"),
    ("Blinkit home decor", "blinkit"),
    ("expensive things on Blinkit", "blinkit"),

    # Platform comparison
    ("Blinkit vs Amazon", "general"),
    ("Blinkit vs Zepto", "general"),
    ("quick commerce India", "general"),

    # Competitors
    ("Zepto haul", "zepto"),
    ("Zepto review", "zepto"),
    ("BigBasket review", "bigbasket"),
]
YOUTUBE_VIDEOS_PER_QUERY = 5
YOUTUBE_COMMENTS_PER_VIDEO = 60

# --- Output paths ---
OUT_PLAYSTORE = "data/playstore_reviews.csv"
OUT_APPSTORE = "data/appstore_reviews.csv"
OUT_REDDIT = "data/reddit_discussions.csv"
OUT_COMPETITORS = "data/competitor_reviews.csv"
OUT_YOUTUBE = "data/youtube_comments.csv"
OUT_COMBINED = "data/all_feedback.csv"
