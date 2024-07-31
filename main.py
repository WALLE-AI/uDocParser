from api.service.conversation_service import test_chat
from handbook.handbook_pdf_parser import handbook_parser
from test.test_aliyun_oss import test_upload_oss
from test.test_cv_llm import test_cv_llm
from test.test_embedding_model import test_embedding_model
from test.test_llm import test_llm_chat, test_openrouter_llm, test_llm_siliconflow_chat
from test.test_llm_service import test_llm_serivices
from test.test_pdf_handbook_paraser import test_handbook_parser
from test.test_rerank import test_rerank_model
from test.test_website_content import test_example

if __name__=="__main__":
    test_cv_llm()