
GC_LOGTYPE_CLOUDAUDIT = 'cloudaudit'
GC_LOGTYPE_ACCESS = 'access'
GC_LOGTYPE_ADMIN = 'admin'
GC_LOGTYPE_CLOUDSUMMARY = 'cloudsummary'

GC_LOGTYPE_SWGWEB = 'swgweb'
GC_LOGTYPE_SWGWEBDLP = 'swgwebdlp'

GC_LOGTYPE_HEALTHPROXY = 'healthproxy'
GC_LOGTYPE_HEALTHAPI = 'healthapi'
GC_LOGTYPE_HEALTHSYSTEM = 'healthsystem'

GC_RESETTIME = 'resettime'

GC_FIELD_LOGTYPE = 'logtype'
GC_FIELD_NEXTPAGETOKEN = 'nextpagetoken'
GC_FIELD_DLPPATTERN = 'dlppattern'
GC_FIELD_EMAIL = 'email'
GC_FIELD_PATTERNS = 'patterns'
GC_FIELD_OWNER = 'owner'
GC_FIELD_TIME = 'time'

GC_FIELD_INGESTEDTIME = '_ingestedtime'
GC_FIELD_INITIALTIME = '_initialtime'


# Phantom

# Regex and datetime patterns
GC_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

# Ingestion run mode constants
GC_ALERT_USER_MATCH_KEY = 'User Alert Matches (by Asset Patterns)'

# Contains for the different artifact keys
GC_BG_USERNAME_CONTAINS = ['user name']

# Error message constants
ERR_CODE_MSG = "Error code unavailable"
ERR_MSG_UNAVAILABLE = "Error message unavailable. Please check the asset configuration and|or action parameters"
PARSE_ERR_MSG = "Unable to parse the error message. Please check the asset configuration and|or action parameters"

# Message constants
INVALID_PARAMS_ERR_MSG = "Please provide valid action parameters value"
INVALID_PARAM_ERR_MSG = "Please provide a valid action parameter value"
