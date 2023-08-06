import sys
import os

sys.path.append(os.path.abspath(__file__))
sys.path.append("/PaperCrawlerUtil/proxypool/")
sys.path.append("/PaperCrawlerUtil/")
__all__ = ["common_util", "crawler_util", "document_util"]
print(sys.path)
from crawler_util import *
from document_util import *
from common_util import *

basic_config(logs_style=LOG_STYLE_PRINT, require_proxy_pool=True)
