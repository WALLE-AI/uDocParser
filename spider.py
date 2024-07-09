import os
import requests
from bs4 import BeautifulSoup
import time
from loguru import logger
from tqdm import tqdm


# 设置基本URL和下载路径
base_url = "http://www.weboos.cn:8083/assets/data/"
download_path = "./pdf_downloads_new/"

# 创建下载目录
if not os.path.exists(download_path):
    os.makedirs(download_path)

# 获取网页内容
response = requests.get(base_url)
soup = BeautifulSoup(response.content, 'html.parser')

# 查找所有PDF链接
links = soup.find_all('a')
pdf_links = [link.text for link in links if link['href'].endswith('.pdf')]

def list_pdf_files_in_directory(directory_path):
    try:
        # 获取目录中的所有文件和子目录
        entries = os.listdir(directory_path)
        
        # 过滤并只保留 PDF 文件
        pdf_files = [entry for entry in entries if entry.lower().endswith('.pdf') and os.path.isfile(os.path.join(directory_path, entry))]        
        return pdf_files
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
pdf_files_local = list_pdf_files_in_directory(download_path)


# 下载所有PDF文件
for pdf_link in tqdm(pdf_links[1:len(pdf_links)-1]):
    pdf_name_id = pdf_link.split("/")[-1]
    if pdf_name_id not in pdf_files_local:
        logger.info(f"download pdf name {pdf_name_id}")
        pdf_url = base_url + pdf_name_id
        pdf_response = requests.get(pdf_url)
        ##延迟两秒
        time.sleep(1)
        # 获取PDF文件名
        pdf_name = os.path.join(download_path, pdf_name_id)
        # 保存PDF文件
        with open(pdf_name, 'wb') as pdf_file:
            logger.info(f"downloading pdf {pdf_name_id}")
            pdf_file.write(pdf_response.content)
    else:
        logger.info(f"pdf name is local exist {pdf_name_id}")
print("All PDF files have been downloaded.")