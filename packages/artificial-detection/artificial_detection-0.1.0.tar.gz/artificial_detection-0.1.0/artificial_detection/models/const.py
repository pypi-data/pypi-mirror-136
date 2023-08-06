import os

BATCH_SIZE = 128
EASY_NMT_MODEL_NAME = "opus-mt"
SRC_LANG = "ru"
TRG_LANG = "en"
LM_LENGTH_LOWER_BOUND = 100
LM_LENGTH_UPPER_BOUND = 350
SEMI_SUPERVISED_HUMAN_RATE = 0.05
SMR_LENGTH_LOWER_BOUND = 20
SMR_REPEAT_RATE = 0.5
COLLECTION_CONCAT_SYMBOL = ". "
ORD_UPPER_BOUND = 500
CLASSIFICATION_THRESHOLD = 0.5
HF_MODEL_NAME = "cointegrated/rubert-tiny"
HF_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources/data/rubert-tiny")

METRIC_NAMES = ["accuracy", "f1", "precision", "recall"]
METRIC_SKLEARN_NAMES = [f"{metric}_score" for metric in METRIC_NAMES]
