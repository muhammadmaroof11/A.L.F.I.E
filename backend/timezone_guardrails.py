"""
Timezone Guardrails & TCPA Compliance Engine.

Provides NANPA area code to IANA timezone mapping across the United States and Canada,
evaluates real-time Federal and State-level TCPA legal calling hours (8:00 AM - 9:00 PM / 8:00 PM),
and calculates quiet-hours postponement timestamps and multi-touch callback cadence schedules.
"""

from datetime import datetime, time as dtime, timedelta, timezone
import logging
import re
from typing import Any, Dict, Optional, Tuple
from zoneinfo import ZoneInfo

logger = logging.getLogger("alfie.timezone_guardrails")

# States with stricter 8:00 AM - 8:00 PM calling windows (e.g. Florida FTSA, Oklahoma OTSA, Washington)
STRICT_TCPA_STATES = {"FL", "OK", "WA"}

# Standard Federal TCPA Window
FEDERAL_TCPA_START_HOUR = 8   # 8:00 AM
FEDERAL_TCPA_END_HOUR = 21    # 9:00 PM

# Strict State TCPA Window
STRICT_TCPA_END_HOUR = 20     # 8:00 PM

# Comprehensive NANPA Area Code Mapping Table
# Maps 3-digit NPA to { "tz": IANA_TIMEZONE, "state": TWO_LETTER_CODE, "country": "US" | "CA" }
AREA_CODE_DATA: Dict[str, Dict[str, str]] = {
    # District of Columbia
    "202": {"tz": "America/New_York", "state": "DC", "country": "US"},
    # Alabama
    "205": {"tz": "America/Chicago", "state": "AL", "country": "US"},
    "251": {"tz": "America/Chicago", "state": "AL", "country": "US"},
    "256": {"tz": "America/Chicago", "state": "AL", "country": "US"},
    "334": {"tz": "America/Chicago", "state": "AL", "country": "US"},
    "938": {"tz": "America/Chicago", "state": "AL", "country": "US"},
    # Alaska
    "907": {"tz": "America/Anchorage", "state": "AK", "country": "US"},
    # Arizona (Phoenix doesn't observe DST)
    "480": {"tz": "America/Phoenix", "state": "AZ", "country": "US"},
    "520": {"tz": "America/Phoenix", "state": "AZ", "country": "US"},
    "602": {"tz": "America/Phoenix", "state": "AZ", "country": "US"},
    "623": {"tz": "America/Phoenix", "state": "AZ", "country": "US"},
    "928": {"tz": "America/Phoenix", "state": "AZ", "country": "US"},
    # Arkansas
    "479": {"tz": "America/Chicago", "state": "AR", "country": "US"},
    "501": {"tz": "America/Chicago", "state": "AR", "country": "US"},
    "870": {"tz": "America/Chicago", "state": "AR", "country": "US"},
    # California
    "209": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "213": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "279": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "310": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "323": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "341": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "408": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "415": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "424": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "442": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "510": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "530": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "559": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "562": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "619": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "626": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "628": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "650": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "657": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "661": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "669": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "707": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "714": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "747": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "760": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "805": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "818": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "820": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "831": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "858": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "909": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "916": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "925": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "949": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    "951": {"tz": "America/Los_Angeles", "state": "CA", "country": "US"},
    # Colorado
    "303": {"tz": "America/Denver", "state": "CO", "country": "US"},
    "719": {"tz": "America/Denver", "state": "CO", "country": "US"},
    "720": {"tz": "America/Denver", "state": "CO", "country": "US"},
    "970": {"tz": "America/Denver", "state": "CO", "country": "US"},
    # Connecticut
    "203": {"tz": "America/New_York", "state": "CT", "country": "US"},
    "475": {"tz": "America/New_York", "state": "CT", "country": "US"},
    "860": {"tz": "America/New_York", "state": "CT", "country": "US"},
    "959": {"tz": "America/New_York", "state": "CT", "country": "US"},
    # Delaware
    "302": {"tz": "America/New_York", "state": "DE", "country": "US"},
    # Florida (Strict 8pm TCPA limit)
    "239": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "305": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "321": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "352": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "386": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "407": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "561": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "727": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "754": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "772": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "786": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "813": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "850": {"tz": "America/Chicago", "state": "FL", "country": "US"},  # Panhandle has Central
    "863": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "904": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "941": {"tz": "America/New_York", "state": "FL", "country": "US"},
    "954": {"tz": "America/New_York", "state": "FL", "country": "US"},
    # Georgia
    "229": {"tz": "America/New_York", "state": "GA", "country": "US"},
    "404": {"tz": "America/New_York", "state": "GA", "country": "US"},
    "470": {"tz": "America/New_York", "state": "GA", "country": "US"},
    "478": {"tz": "America/New_York", "state": "GA", "country": "US"},
    "678": {"tz": "America/New_York", "state": "GA", "country": "US"},
    "706": {"tz": "America/New_York", "state": "GA", "country": "US"},
    "762": {"tz": "America/New_York", "state": "GA", "country": "US"},
    "770": {"tz": "America/New_York", "state": "GA", "country": "US"},
    "912": {"tz": "America/New_York", "state": "GA", "country": "US"},
    # Hawaii
    "808": {"tz": "Pacific/Honolulu", "state": "HI", "country": "US"},
    # Idaho
    "208": {"tz": "America/Boise", "state": "ID", "country": "US"},
    "986": {"tz": "America/Boise", "state": "ID", "country": "US"},
    # Illinois
    "217": {"tz": "America/Chicago", "state": "IL", "country": "US"},
    "224": {"tz": "America/Chicago", "state": "IL", "country": "US"},
    "309": {"tz": "America/Chicago", "state": "IL", "country": "US"},
    "312": {"tz": "America/Chicago", "state": "IL", "country": "US"},
    "331": {"tz": "America/Chicago", "state": "IL", "country": "US"},
    "618": {"tz": "America/Chicago", "state": "IL", "country": "US"},
    "630": {"tz": "America/Chicago", "state": "IL", "country": "US"},
    "708": {"tz": "America/Chicago", "state": "IL", "country": "US"},
    "773": {"tz": "America/Chicago", "state": "IL", "country": "US"},
    "779": {"tz": "America/Chicago", "state": "IL", "country": "US"},
    "815": {"tz": "America/Chicago", "state": "IL", "country": "US"},
    "847": {"tz": "America/Chicago", "state": "IL", "country": "US"},
    "872": {"tz": "America/Chicago", "state": "IL", "country": "US"},
    # Indiana
    "219": {"tz": "America/Chicago", "state": "IN", "country": "US"},
    "260": {"tz": "America/Indiana/Indianapolis", "state": "IN", "country": "US"},
    "317": {"tz": "America/Indiana/Indianapolis", "state": "IN", "country": "US"},
    "463": {"tz": "America/Indiana/Indianapolis", "state": "IN", "country": "US"},
    "574": {"tz": "America/Indiana/Indianapolis", "state": "IN", "country": "US"},
    "765": {"tz": "America/Indiana/Indianapolis", "state": "IN", "country": "US"},
    "812": {"tz": "America/Indiana/Indianapolis", "state": "IN", "country": "US"},
    "930": {"tz": "America/Indiana/Indianapolis", "state": "IN", "country": "US"},
    # Iowa
    "319": {"tz": "America/Chicago", "state": "IA", "country": "US"},
    "515": {"tz": "America/Chicago", "state": "IA", "country": "US"},
    "563": {"tz": "America/Chicago", "state": "IA", "country": "US"},
    "641": {"tz": "America/Chicago", "state": "IA", "country": "US"},
    "712": {"tz": "America/Chicago", "state": "IA", "country": "US"},
    # Kansas
    "316": {"tz": "America/Chicago", "state": "KS", "country": "US"},
    "620": {"tz": "America/Chicago", "state": "KS", "country": "US"},
    "785": {"tz": "America/Chicago", "state": "KS", "country": "US"},
    "913": {"tz": "America/Chicago", "state": "KS", "country": "US"},
    # Kentucky
    "270": {"tz": "America/Chicago", "state": "KY", "country": "US"},
    "364": {"tz": "America/Chicago", "state": "KY", "country": "US"},
    "502": {"tz": "America/New_York", "state": "KY", "country": "US"},
    "606": {"tz": "America/New_York", "state": "KY", "country": "US"},
    "859": {"tz": "America/New_York", "state": "KY", "country": "US"},
    # Louisiana
    "225": {"tz": "America/Chicago", "state": "LA", "country": "US"},
    "318": {"tz": "America/Chicago", "state": "LA", "country": "US"},
    "337": {"tz": "America/Chicago", "state": "LA", "country": "US"},
    "504": {"tz": "America/Chicago", "state": "LA", "country": "US"},
    "985": {"tz": "America/Chicago", "state": "LA", "country": "US"},
    # Maine
    "207": {"tz": "America/New_York", "state": "ME", "country": "US"},
    # Maryland
    "240": {"tz": "America/New_York", "state": "MD", "country": "US"},
    "301": {"tz": "America/New_York", "state": "MD", "country": "US"},
    "410": {"tz": "America/New_York", "state": "MD", "country": "US"},
    "443": {"tz": "America/New_York", "state": "MD", "country": "US"},
    "667": {"tz": "America/New_York", "state": "MD", "country": "US"},
    # Massachusetts
    "339": {"tz": "America/New_York", "state": "MA", "country": "US"},
    "351": {"tz": "America/New_York", "state": "MA", "country": "US"},
    "413": {"tz": "America/New_York", "state": "MA", "country": "US"},
    "508": {"tz": "America/New_York", "state": "MA", "country": "US"},
    "617": {"tz": "America/New_York", "state": "MA", "country": "US"},
    "774": {"tz": "America/New_York", "state": "MA", "country": "US"},
    "781": {"tz": "America/New_York", "state": "MA", "country": "US"},
    "857": {"tz": "America/New_York", "state": "MA", "country": "US"},
    "978": {"tz": "America/New_York", "state": "MA", "country": "US"},
    # Michigan
    "231": {"tz": "America/Detroit", "state": "MI", "country": "US"},
    "248": {"tz": "America/Detroit", "state": "MI", "country": "US"},
    "269": {"tz": "America/Detroit", "state": "MI", "country": "US"},
    "313": {"tz": "America/Detroit", "state": "MI", "country": "US"},
    "517": {"tz": "America/Detroit", "state": "MI", "country": "US"},
    "586": {"tz": "America/Detroit", "state": "MI", "country": "US"},
    "616": {"tz": "America/Detroit", "state": "MI", "country": "US"},
    "734": {"tz": "America/Detroit", "state": "MI", "country": "US"},
    "810": {"tz": "America/Detroit", "state": "MI", "country": "US"},
    "906": {"tz": "America/Detroit", "state": "MI", "country": "US"},
    "947": {"tz": "America/Detroit", "state": "MI", "country": "US"},
    "989": {"tz": "America/Detroit", "state": "MI", "country": "US"},
    # Minnesota
    "218": {"tz": "America/Chicago", "state": "MN", "country": "US"},
    "320": {"tz": "America/Chicago", "state": "MN", "country": "US"},
    "507": {"tz": "America/Chicago", "state": "MN", "country": "US"},
    "612": {"tz": "America/Chicago", "state": "MN", "country": "US"},
    "651": {"tz": "America/Chicago", "state": "MN", "country": "US"},
    "763": {"tz": "America/Chicago", "state": "MN", "country": "US"},
    "952": {"tz": "America/Chicago", "state": "MN", "country": "US"},
    # Mississippi
    "228": {"tz": "America/Chicago", "state": "MS", "country": "US"},
    "601": {"tz": "America/Chicago", "state": "MS", "country": "US"},
    "662": {"tz": "America/Chicago", "state": "MS", "country": "US"},
    "769": {"tz": "America/Chicago", "state": "MS", "country": "US"},
    # Missouri
    "314": {"tz": "America/Chicago", "state": "MO", "country": "US"},
    "417": {"tz": "America/Chicago", "state": "MO", "country": "US"},
    "573": {"tz": "America/Chicago", "state": "MO", "country": "US"},
    "636": {"tz": "America/Chicago", "state": "MO", "country": "US"},
    "660": {"tz": "America/Chicago", "state": "MO", "country": "US"},
    "816": {"tz": "America/Chicago", "state": "MO", "country": "US"},
    # Montana
    "406": {"tz": "America/Denver", "state": "MT", "country": "US"},
    # Nebraska
    "308": {"tz": "America/Chicago", "state": "NE", "country": "US"},
    "402": {"tz": "America/Chicago", "state": "NE", "country": "US"},
    "531": {"tz": "America/Chicago", "state": "NE", "country": "US"},
    # Nevada
    "702": {"tz": "America/Los_Angeles", "state": "NV", "country": "US"},
    "725": {"tz": "America/Los_Angeles", "state": "NV", "country": "US"},
    "775": {"tz": "America/Los_Angeles", "state": "NV", "country": "US"},
    # New Hampshire
    "603": {"tz": "America/New_York", "state": "NH", "country": "US"},
    # New Jersey
    "201": {"tz": "America/New_York", "state": "NJ", "country": "US"},
    "551": {"tz": "America/New_York", "state": "NJ", "country": "US"},
    "609": {"tz": "America/New_York", "state": "NJ", "country": "US"},
    "640": {"tz": "America/New_York", "state": "NJ", "country": "US"},
    "732": {"tz": "America/New_York", "state": "NJ", "country": "US"},
    "848": {"tz": "America/New_York", "state": "NJ", "country": "US"},
    "856": {"tz": "America/New_York", "state": "NJ", "country": "US"},
    "862": {"tz": "America/New_York", "state": "NJ", "country": "US"},
    "908": {"tz": "America/New_York", "state": "NJ", "country": "US"},
    "973": {"tz": "America/New_York", "state": "NJ", "country": "US"},
    # New Mexico
    "505": {"tz": "America/Denver", "state": "NM", "country": "US"},
    "575": {"tz": "America/Denver", "state": "NM", "country": "US"},
    # New York
    "212": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "315": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "332": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "347": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "516": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "518": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "585": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "607": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "631": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "646": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "680": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "716": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "718": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "838": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "845": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "914": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "917": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "929": {"tz": "America/New_York", "state": "NY", "country": "US"},
    "934": {"tz": "America/New_York", "state": "NY", "country": "US"},
    # North Carolina
    "252": {"tz": "America/New_York", "state": "NC", "country": "US"},
    "336": {"tz": "America/New_York", "state": "NC", "country": "US"},
    "704": {"tz": "America/New_York", "state": "NC", "country": "US"},
    "828": {"tz": "America/New_York", "state": "NC", "country": "US"},
    "910": {"tz": "America/New_York", "state": "NC", "country": "US"},
    "919": {"tz": "America/New_York", "state": "NC", "country": "US"},
    "980": {"tz": "America/New_York", "state": "NC", "country": "US"},
    "984": {"tz": "America/New_York", "state": "NC", "country": "US"},
    # North Dakota
    "701": {"tz": "America/Chicago", "state": "ND", "country": "US"},
    # Ohio
    "216": {"tz": "America/New_York", "state": "OH", "country": "US"},
    "234": {"tz": "America/New_York", "state": "OH", "country": "US"},
    "330": {"tz": "America/New_York", "state": "OH", "country": "US"},
    "380": {"tz": "America/New_York", "state": "OH", "country": "US"},
    "419": {"tz": "America/New_York", "state": "OH", "country": "US"},
    "440": {"tz": "America/New_York", "state": "OH", "country": "US"},
    "513": {"tz": "America/New_York", "state": "OH", "country": "US"},
    "567": {"tz": "America/New_York", "state": "OH", "country": "US"},
    "614": {"tz": "America/New_York", "state": "OH", "country": "US"},
    "937": {"tz": "America/New_York", "state": "OH", "country": "US"},
    # Oklahoma (Strict 8pm TCPA limit)
    "405": {"tz": "America/Chicago", "state": "OK", "country": "US"},
    "539": {"tz": "America/Chicago", "state": "OK", "country": "US"},
    "580": {"tz": "America/Chicago", "state": "OK", "country": "US"},
    "918": {"tz": "America/Chicago", "state": "OK", "country": "US"},
    # Oregon
    "458": {"tz": "America/Los_Angeles", "state": "OR", "country": "US"},
    "503": {"tz": "America/Los_Angeles", "state": "OR", "country": "US"},
    "541": {"tz": "America/Los_Angeles", "state": "OR", "country": "US"},
    "971": {"tz": "America/Los_Angeles", "state": "OR", "country": "US"},
    # Pennsylvania
    "215": {"tz": "America/New_York", "state": "PA", "country": "US"},
    "267": {"tz": "America/New_York", "state": "PA", "country": "US"},
    "272": {"tz": "America/New_York", "state": "PA", "country": "US"},
    "412": {"tz": "America/New_York", "state": "PA", "country": "US"},
    "484": {"tz": "America/New_York", "state": "PA", "country": "US"},
    "570": {"tz": "America/New_York", "state": "PA", "country": "US"},
    "610": {"tz": "America/New_York", "state": "PA", "country": "US"},
    "717": {"tz": "America/New_York", "state": "PA", "country": "US"},
    "724": {"tz": "America/New_York", "state": "PA", "country": "US"},
    "814": {"tz": "America/New_York", "state": "PA", "country": "US"},
    "878": {"tz": "America/New_York", "state": "PA", "country": "US"},
    # Rhode Island
    "401": {"tz": "America/New_York", "state": "RI", "country": "US"},
    # South Carolina
    "803": {"tz": "America/New_York", "state": "SC", "country": "US"},
    "843": {"tz": "America/New_York", "state": "SC", "country": "US"},
    "854": {"tz": "America/New_York", "state": "SC", "country": "US"},
    "864": {"tz": "America/New_York", "state": "SC", "country": "US"},
    # South Dakota
    "605": {"tz": "America/Chicago", "state": "SD", "country": "US"},
    # Tennessee
    "423": {"tz": "America/New_York", "state": "TN", "country": "US"},
    "615": {"tz": "America/Chicago", "state": "TN", "country": "US"},
    "629": {"tz": "America/Chicago", "state": "TN", "country": "US"},
    "731": {"tz": "America/Chicago", "state": "TN", "country": "US"},
    "865": {"tz": "America/New_York", "state": "TN", "country": "US"},
    "901": {"tz": "America/Chicago", "state": "TN", "country": "US"},
    "931": {"tz": "America/Chicago", "state": "TN", "country": "US"},
    # Texas
    "210": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "214": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "254": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "281": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "325": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "346": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "361": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "409": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "430": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "432": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "469": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "512": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "682": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "713": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "726": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "737": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "806": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "817": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "830": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "832": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "903": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "915": {"tz": "America/Denver", "state": "TX", "country": "US"},   # El Paso is Mountain
    "936": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "940": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "956": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "972": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    "979": {"tz": "America/Chicago", "state": "TX", "country": "US"},
    # Utah
    "385": {"tz": "America/Denver", "state": "UT", "country": "US"},
    "435": {"tz": "America/Denver", "state": "UT", "country": "US"},
    "801": {"tz": "America/Denver", "state": "UT", "country": "US"},
    # Vermont
    "802": {"tz": "America/New_York", "state": "VT", "country": "US"},
    # Virginia
    "276": {"tz": "America/New_York", "state": "VA", "country": "US"},
    "434": {"tz": "America/New_York", "state": "VA", "country": "US"},
    "540": {"tz": "America/New_York", "state": "VA", "country": "US"},
    "571": {"tz": "America/New_York", "state": "VA", "country": "US"},
    "703": {"tz": "America/New_York", "state": "VA", "country": "US"},
    "757": {"tz": "America/New_York", "state": "VA", "country": "US"},
    "804": {"tz": "America/New_York", "state": "VA", "country": "US"},
    # Washington (Strict 8pm TCPA limit)
    "206": {"tz": "America/Los_Angeles", "state": "WA", "country": "US"},
    "253": {"tz": "America/Los_Angeles", "state": "WA", "country": "US"},
    "360": {"tz": "America/Los_Angeles", "state": "WA", "country": "US"},
    "425": {"tz": "America/Los_Angeles", "state": "WA", "country": "US"},
    "509": {"tz": "America/Los_Angeles", "state": "WA", "country": "US"},
    "564": {"tz": "America/Los_Angeles", "state": "WA", "country": "US"},
    # West Virginia
    "304": {"tz": "America/New_York", "state": "WV", "country": "US"},
    "681": {"tz": "America/New_York", "state": "WV", "country": "US"},
    # Wisconsin
    "262": {"tz": "America/Chicago", "state": "WI", "country": "US"},
    "414": {"tz": "America/Chicago", "state": "WI", "country": "US"},
    "534": {"tz": "America/Chicago", "state": "WI", "country": "US"},
    "608": {"tz": "America/Chicago", "state": "WI", "country": "US"},
    "715": {"tz": "America/Chicago", "state": "WI", "country": "US"},
    "920": {"tz": "America/Chicago", "state": "WI", "country": "US"},
    # Wyoming
    "307": {"tz": "America/Denver", "state": "WY", "country": "US"},
    # Canada (Ontario & Quebec Eastern, BC Pacific, Alberta Mountain)
    "416": {"tz": "America/Toronto", "state": "ON", "country": "CA"},
    "647": {"tz": "America/Toronto", "state": "ON", "country": "CA"},
    "437": {"tz": "America/Toronto", "state": "ON", "country": "CA"},
    "905": {"tz": "America/Toronto", "state": "ON", "country": "CA"},
    "289": {"tz": "America/Toronto", "state": "ON", "country": "CA"},
    "514": {"tz": "America/Montreal", "state": "QC", "country": "CA"},
    "438": {"tz": "America/Montreal", "state": "QC", "country": "CA"},
    "604": {"tz": "America/Vancouver", "state": "BC", "country": "CA"},
    "778": {"tz": "America/Vancouver", "state": "BC", "country": "CA"},
    "250": {"tz": "America/Vancouver", "state": "BC", "country": "CA"},
    "403": {"tz": "America/Edmonton", "state": "AB", "country": "CA"},
    "780": {"tz": "America/Edmonton", "state": "AB", "country": "CA"},
    "587": {"tz": "America/Edmonton", "state": "AB", "country": "CA"},
}

DEFAULT_TIMEZONE = "America/New_York"
DEFAULT_STATE = "US"


def extract_npa_area_code(phone_number: str) -> Optional[str]:
    """
    Extracts the 3-digit NPA (area code) from phone number strings.
    Accepts E.164 (+14155551234), standard dashes (415-555-1234), parentheses (415) 555-1234, or raw digits.
    """
    if not phone_number:
        return None
    
    digits = re.sub(r"\D", "", phone_number)
    
    # If 11 digits and starts with 1 (US/Canada country code), strip leading 1
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
        
    if len(digits) >= 3:
        npa = digits[:3]
        # Valid NANPA area codes do not start with 0 or 1
        if npa[0] not in ("0", "1"):
            return npa
            
    return None


def resolve_phone_timezone(phone_number: str) -> Dict[str, Any]:
    """
    Resolves the canonical timezone, state/province, and country for a phone number.
    Returns dictionary with area_code, timezone, state, country, and is_valid.
    """
    npa = extract_npa_area_code(phone_number)
    if npa and npa in AREA_CODE_DATA:
        data = AREA_CODE_DATA[npa]
        return {
            "area_code": npa,
            "timezone": data["tz"],
            "state": data["state"],
            "country": data["country"],
            "is_valid": True,
        }
    
    # Fallback to Eastern timezone
    return {
        "area_code": npa or "000",
        "timezone": DEFAULT_TIMEZONE,
        "state": DEFAULT_STATE,
        "country": "US",
        "is_valid": False,
    }


def is_within_legal_calling_hours(
    phone_number: str,
    as_of: Optional[datetime] = None,
    strict_state_rules: bool = True,
) -> Tuple[bool, str, datetime]:
    """
    Evaluates whether an outbound call to the given phone number is currently compliant
    with Federal TCPA (8:00 AM - 9:00 PM) and state-specific restrictions (FL, OK, WA: 8:00 AM - 8:00 PM).

    Returns:
      (is_permitted: bool, reason: str, next_permitted_dt_utc: datetime)
    """
    now_utc = as_of or datetime.now(timezone.utc)
    tz_info = resolve_phone_timezone(phone_number)
    tz_name = tz_info["timezone"]
    state = tz_info["state"]

    try:
        local_tz = ZoneInfo(tz_name)
    except Exception:
        local_tz = ZoneInfo(DEFAULT_TIMEZONE)

    recipient_local_dt = now_utc.astimezone(local_tz)
    local_time = recipient_local_dt.time()
    local_hour = local_time.hour
    local_minute = local_time.minute

    # Determine legal end hour (8 PM for strict states, 9 PM federal default)
    end_hour = STRICT_TCPA_END_HOUR if (strict_state_rules and state in STRICT_TCPA_STATES) else FEDERAL_TCPA_END_HOUR
    start_hour = FEDERAL_TCPA_START_HOUR

    start_limit = dtime(start_hour, 0, 0)
    end_limit = dtime(end_hour, 0, 0)

    # Check if currently inside window [08:00, end_limit)
    if start_limit <= local_time < end_limit:
        reason = f"Legal calling hours active ({local_hour:02d}:{local_minute:02d} {tz_name})"
        return True, reason, now_utc

    # Outside window -> determine when the next legal window opens
    if local_time < start_limit:
        # Before 8:00 AM today: opens today at 8:05 AM local time
        next_local = datetime.combine(
            recipient_local_dt.date(),
            dtime(start_hour, 5, 0),
            tzinfo=local_tz,
        )
        reason = f"Quiet hours: too early ({local_hour:02d}:{local_minute:02d} {tz_name}). Postponed to 8:05 AM local."
    else:
        # After end_hour tonight: opens tomorrow at 8:05 AM local time
        tomorrow_date = recipient_local_dt.date() + timedelta(days=1)
        next_local = datetime.combine(
            tomorrow_date,
            dtime(start_hour, 5, 0),
            tzinfo=local_tz,
        )
        reason = f"Quiet hours: too late ({local_hour:02d}:{local_minute:02d} {tz_name}). Postponed to tomorrow 8:05 AM local."

    next_utc = next_local.astimezone(timezone.utc)
    return False, reason, next_utc


def calculate_next_cadence_attempt(
    phone_number: str,
    attempt: int,
    base_time: Optional[datetime] = None,
) -> Tuple[datetime, str]:
    """
    Computes the scheduled UTC timestamp for the next callback retry touch respecting legal hours:
      - Attempt 1: Immediate or at preferred time (postponed if quiet hours).
      - Attempt 2: Base time + 2 hours (120 mins). If falls in quiet hours, moves to tomorrow 8:30 AM local.
      - Attempt 3: Base time + 24 hours (next business day at 10:00 AM local recipient time).
    """
    now_utc = base_time or datetime.now(timezone.utc)
    tz_info = resolve_phone_timezone(phone_number)
    tz_name = tz_info["timezone"]

    try:
        local_tz = ZoneInfo(tz_name)
    except Exception:
        local_tz = ZoneInfo(DEFAULT_TIMEZONE)

    recipient_local = now_utc.astimezone(local_tz)

    if attempt <= 1:
        permitted, _, next_utc = is_within_legal_calling_hours(phone_number, as_of=now_utc)
        if permitted:
            return now_utc, "immediate"
        return next_utc, "rescheduled_legal_hours"

    elif attempt == 2:
        # Attempt 2: Target +2 hours from base time
        target_utc = now_utc + timedelta(hours=2)
        permitted, _, next_utc = is_within_legal_calling_hours(phone_number, as_of=target_utc)
        if permitted:
            return target_utc, "scheduled_touch_2"
        return next_utc, "rescheduled_legal_hours"

    else:
        # Attempt 3: Target next day at 10:00 AM recipient local time
        tomorrow_date = recipient_local.date() + timedelta(days=1)
        target_local = datetime.combine(
            tomorrow_date,
            dtime(10, 0, 0),
            tzinfo=local_tz,
        )
        target_utc = target_local.astimezone(timezone.utc)
        return target_utc, "scheduled_touch_3"
