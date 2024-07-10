import openai
import os
import threading
import httpx

from llm_config import MODEL_NAME_LIST

class LLMApi():
    def __init__(self) -> None:
        self.des = "llm api service"
    def __str__(self) -> str:
        return self.des
    
    def init_client_config(self,llm_type):
        if llm_type == "openrouter":
            base_url = "https://openrouter.ai/api/v1"
            api_key  = os.environ.get("OPENROUTER_API_KEY")
        elif llm_type =='siliconflow':
            base_url = "https://api.siliconflow.cn/v1"
            api_key = os.environ.get("SILICONFLOW_API_KEY")
        else:
            base_url = "https://api.openai.com/v1"
            api_key  = os.environ.get("OPENAI_API_KEY")
        return base_url,api_key     
            
    def llm_client(self,llm_type):
        base_url,api_key = self.init_client_config(llm_type)
        thread_local = threading.local()
        try:
            return thread_local.client
        except AttributeError:
            thread_local.client = openai.OpenAI(
                base_url=base_url,
                api_key=api_key,
                # We will set the connect timeout to be 10 seconds, and read/write
                # timeout to be 120 seconds, in case the inference server is
                # overloaded.
                timeout=httpx.Timeout(connect=10, read=120, write=120, pool=10),
            )
            return thread_local.client
    @classmethod
    def llm_result_postprocess(cls,llm_response):
        from json_repair import repair_json
        json_string = repair_json(llm_response.choices[0].message.content,return_objects=True)
        return json_string 
    
    @classmethod
    def call_llm(cls,prompt,stream=False,llm_type="siliconflow",model_name="Qwen/Qwen2-7B-Instruct"):
        '''
        默认选择siliconflow qwen2-72B的模型来
        '''
        llm_response = cls.get_client(llm_type=llm_type).chat.completions.create(
                model=MODEL_NAME_LIST[llm_type][model_name],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                stream=stream,
                temperature=0.2,
            )
        return llm_response

    @classmethod    
    def get_client(cls,llm_type):
        return cls().llm_client(llm_type)
    
    
if __name__ == "__main__":
    result = LLMApi.call_llm("你是谁")
    result = LLMApi.llm_result_postprocess(result)
    print(result)


        