# Char
from locale import getdefaultlocale


def getChar():
    char = getdefaultlocale()[0].lower()
    if "zh" in char:
        DEPLOY_LANGUAGE = "cn"
    else:
        DEPLOY_LANGUAGE = "en"
    return DEPLOY_LANGUAGE


CHECK_INTERVAL = 20
DEPLOY_LANGUAGE = getChar()
LAIPVT_BASE_DIR = "/usr/local/laipvt"
CHECK_FILE = "/usr/local/laipvt/check_result.yaml"
PRE_CHECK_RESULT_FILE = "/usr/local/laipvt/.precheck_result.yaml"
PORT_MAP = "/usr/local/laipvt/ports.yaml"
STATUS_FILE = "/usr/local/laipvt/.deploy_status"
PROJECT_INFO_FILE = "/usr/local/laipvt/project"
UPGRADE_INFO_FILE = "/usr/local/laipvt/upgrade"
ENTUC_JSON_FILE = "/usr/local/laipvt/entuc.json"

# LOG
LAIPVT_LOG_PATH = "/usr/local/laipvt/logs"
LAIPVT_LOG_NAME = "laipvt.log"
LAIPVT_LOG_LEVEL = "DEBUG"
LOG_TO_TTY = True

# Certs
CERTS_PATH = "/usr/local/laipvt/certs"

# Precheck temp
CHECK_TEMP = "/tmp"
