
# ---------- MULTIRAG --------------------------
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

EXCEPTED_FILE_TYPE=['txt','pdf','http']

RETREIVER_DEFAULT_K=3

LOGS_DIR="logs"
LLM_MODEL_ID = "us.meta.llama3-3-70b-instruct-v1:0"
LLM_REGION = "us-east-1"
MODEL_NAME="llama-3.3-70b-versatile"

TOP_K_KEYWORDS=10

CONTENT_PERSISTENT_TIME=60 # 5 MIN
DATA_FOLDER_PATH="data"
DB_FOLDER_PATH="db"



AVAILABLE_ANALYSIS=['pdf','txt','docs','docx','png','url']



# ====================== DB =======================
DB_FOLDER_PATH="db"



# ====================== Tool ======================
SEARCH_MAX_RESULT=5
SEARCH_TOPIC='general'



