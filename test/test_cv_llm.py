import mimetypes
import os

import loguru

from llm import CvModel
from llm.prompt.prompt_ai_building import PROMPT_AI_BUILDING

api_key = os.environ.get("OPENROUTER_API_KEY")
base_url = "https://openrouter.ai/api/v1"
model_name="openai/gpt-4o-mini-2024-07-18"

def get_mime_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type
def test_cv_llm():
    images_path = "examples\\images_test\\01.png"
    check_result = get_mime_type(images_path)
    cv_model = CvModel['OpenRouter'](key=api_key,model_name=model_name,base_url=base_url)
    with open(images_path, 'rb') as f:
        img_data = f.read()
        response,tokens = cv_model.describe(img_data,prompt=PROMPT_AI_BUILDING,json_format=True)
    loguru.logger.info(f"repsonse:{response},use_tokens:{tokens}")
    return response,tokens