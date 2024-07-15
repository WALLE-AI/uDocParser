import os

import loguru

from llm import CvModel

api_key = os.environ.get("OPENROUTER_API_KEY")
base_url = "https://openrouter.ai/api/v1"
model_name="openai/gpt-4-vision-preview"


def test_cv_llm():
    images_path = "layouts_outputs/test.png"
    cv_model = CvModel['OpenrouterClientCV'](key=api_key,model_name=model_name,base_url=base_url)
    with open(images_path, 'rb') as f:
        img_data = f.read()
        response,tokens = cv_model.describe(img_data)
    loguru.logger.info(f"reponse:{response}，tokens:{tokens}")