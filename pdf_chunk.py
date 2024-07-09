import os
openai_key = os.environ["OPENAI_API_KEY"]
from loguru import logger

from unstructured.partition.pdf import partition_pdf
from langchain.text_splitter import RecursiveCharacterTextSplitter

file_name_path = "pdf/ASurvey on RAGMeetsLLMs Towards Retrieval-Augmented.pdf"

text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=100,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
)



elements = partition_pdf(
    filename="D:/LLM/需求梳理/datasets/建筑行业施工与安全标准/2、GB50108-2008地下工程防水技术规范.pdf",                  # mandatory
    strategy="hi_res",                                     # mandatory to use ``hi_res`` strategy
    extract_images_in_pdf=True,                            # mandatory to set as ``True``
    extract_image_block_types=["Image", "Table"],          # optional
    extract_image_block_to_payload=False,                  # optional
    extract_image_block_output_dir="pdf_test/images",  # optional - only works when ``extract_image_block_to_payload=False``
    )

text = "\n\n".join([str(el) for el in elements][:30])
logger.info(f"context:{text}")
texts = text_splitter.create_documents([text])
print("text:{}".format(texts[:5]))

