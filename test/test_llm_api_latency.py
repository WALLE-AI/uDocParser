from google.colab import userdata
##https://mp.weixin.qq.com/s/UFji5m3Ji1gvsQXqDTy9NQ?wxwork_userid=JiaWei 参考

models_venti ={
'GPT':{
  'brand':'OpenAI',
  'model_version':'gpt-4',
  'api_key' : userdata.get("Key_OpenAI"),
  'base_url' : "https://api.openai.com/v1",
  },
'Moonshot':{
  'brand':'月之暗面',
  'model_version':'moonshot-v1-32k',
  'api_key' : userdata.get("Key_Moonshot"),
  'base_url' : "https://api.moonshot.cn/v1",
  },
'Zhipu':{
  'brand':'智谱',
  'model_version':'glm-4',
  'api_key' : userdata.get("Key_Zhipu"),
  'base_url' : "https://open.bigmodel.cn/api/paas/v4/",
  },
'Qwen':{
  'brand':'通义千问',
  'model_version':'qwen-max',
  'api_key' : userdata.get("Key_Qwen"),
  'base_url' : "https://dashscope.aliyuncs.com/compatible-mode/v1",
  },
'DeepSeek':{
  'brand':'深度求索',
  'model_version':"deepseek-chat",
  'api_key' : userdata.get("Key_DeepSeek"),
  'base_url' : "https://api.deepseek.com",
  },
'Stepfun':{
  'brand':'阶跃星辰',
  'model_version':'step-1-8k',
  'api_key' : userdata.get("Key_Stepfun"),
  'base_url' : "https://api.stepfun.com/v1",
  },
'Baichuan':{
  'brand':'百川',
  'model_version':'Baichuan4',
  'api_key' : userdata.get("Key_Baichuan"),
  'base_url' : "https://api.baichuan-ai.com/v1",
  },
}


models_grande ={
'GPT':{
  'brand':'OpenAI',
  'model_version':'gpt-4o',
  'api_key' : userdata.get("Key_OpenAI"),
  'base_url' : "https://api.openai.com/v1",
  },
'Zhipu':{
  'brand':'智谱',
  'model_version':'glm-4-airx',
  'api_key' : userdata.get("Key_Zhipu"),
  'base_url' : "https://open.bigmodel.cn/api/paas/v4/",
  },
'Qwen':{
  'brand':'通义千问',
  'model_version':'qwen-plus',
  'api_key' : userdata.get("Key_Qwen"),
  'base_url' : "https://dashscope.aliyuncs.com/compatible-mode/v1",
  },
}

models_tall ={
'GPT':{
  'brand':'OpenAI',
  'model_version':'gpt-3.5-turbo',
  'api_key' : userdata.get("Key_OpenAI"),
  'base_url' : "https://api.openai.com/v1",
  },
'Zhipu':{
  'brand':'智谱',
  'model_version':'glm-4-flash',
  'api_key' : userdata.get("Key_Zhipu"),
  'base_url' : "https://open.bigmodel.cn/api/paas/v4/",
  },
'Qwen':{
  'brand':'通义千问',
  'model_version':'qwen-turbo',
  'api_key' : userdata.get("Key_Qwen"),
  'base_url' : "https://dashscope.aliyuncs.com/compatible-mode/v1",
  },
'Baichuan':{
  'brand':'百川',
  'model_version':'Baichuan3-Turbo',
  'api_key' : userdata.get("Key_Baichuan"),
  'base_url' : "https://api.baichuan-ai.com/v1",
  },
}


# 逻辑部分
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
import queue
import time
import datetime
import pytz

def LLM(messages, model, result_dict, use_streaming=False):
    client = OpenAI(
        api_key=model['api_key'],
        base_url=model['base_url'],
    )

    api_params = {
        "model": model['model_version'],
        "messages": messages,
        "stream": use_streaming,
    }

    start_time = time.time()

    try:
        response = client.chat.completions.create(**api_params)
        if use_streaming:
            for chunk in response:
                infer_time = time.time() - start_time
                response.close()
                result = result_dict.get(model['model_version'], {'model': model})
                result.update({
                    'content': None,
                    'duration': infer_time,
                    'use_streaming': use_streaming,
                    'infer_time': infer_time,
                })
                result_dict[model['model_version']] = result
                return
        else:
            result_message = response.choices[0].message
            content = result_message.content or f"蚌埠住了：{model['model_version']} 啥也没说"
            completion_tokens = response.usage.completion_tokens
            prompt_tokens = response.usage.prompt_tokens
            total_tokens = response.usage.total_tokens
            total_time = time.time() - start_time

            result = result_dict.get(model['model_version'], {'model': model})
            result.update({
                'content': content[:20]+'...',
                'duration': total_time,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'use_streaming': use_streaming,
                'generation_time': total_time - result.get('infer_time', 0),
            })
            if 'infer_time' in result:
                result['infer_speed'] = prompt_tokens / result['infer_time'] if result['infer_time'] > 0 else 0
                result['generation_speed'] = completion_tokens / result['generation_time'] if result['generation_time'] > 0 else 0
            result_dict[model['model_version']] = result
            return
    except Exception as e:
        result_dict[model['model_version']] = {
            'model': model,
            'content': f"Error: {e}",
            'use_streaming': use_streaming,
        }

def testALL(messages=[], prompts=[], models={}):
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.datetime.now(tz)
    print(f"\n测试开始时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n")

    result_dict = {}

    def process_messages(messages, use_streaming):
        futures = [executor.submit(LLM, messages, models[key], result_dict, use_streaming) for key in models]
        for future in as_completed(futures):
            future.result()  # Ensure future completes

    with ThreadPoolExecutor() as executor:
        for use_streaming in [True, False]:
            if prompts:
                for prompt in prompts:
                    messages = [{"role": "user", "content": prompt}]
                    process_messages(messages, use_streaming)
            else:
                process_messages(messages, use_streaming)

    # 对结果按生成速度从高到低排序并输出
    sorted_results = sorted(result_dict.values(), key=lambda x: x.get('generation_speed', 0), reverse=True)
    for result in sorted_results:
        print(f"来自「{result['model']['brand']}」的 {result['model']['model_version']}:")
        print(f"上下文总长度：{result['total_tokens']}，用时：{result.get('duration', 0):.2f} 秒")
        print(f"内容：{result.get('content', '无输出')}")
        print(f"输入 token：{result['prompt_tokens']}")
        print(f"输入解析（含网络延迟）：{result.get('infer_time', 0):.2f} 秒")
        print(f"输出 token：{result['completion_tokens']}")
        print(f"生成用时：{result.get('generation_time', 0):.2f} 秒，生成速度：{result.get('generation_speed', 0):.2f} token/s")
        print("\n")
        

# 执行部分
prompts = [
    """将以下内容，翻译成现代汉语：先帝创业未半而中道崩殂，今天下三分，益州疲弊，此诚危急存亡之秋也。然侍卫之臣不懈于内，忠志之士忘身于外者，盖追先帝之殊遇，欲报之于陛下也。诚宜开张圣听，以光先帝遗德，恢弘志士之气，不宜妄自菲薄，引喻失义，以塞忠谏之路也。

宫中府中，俱为一体，陟罚臧否，不宜异同。若有作奸犯科及为忠善者，宜付有司论其刑赏，以昭陛下平明之理，不宜偏私，使内外异法也。

侍中、侍郎郭攸之、费祎、董允等，此皆良实，志虑忠纯，是以先帝简拔以遗陛下。愚以为宫中之事，事无大小，悉以咨之，然后施行，必能裨补阙漏，有所广益。

将军向宠，性行淑均，晓畅军事，试用于昔日，先帝称之曰能，是以众议举宠为督。愚以为营中之事，悉以咨之，必能使行阵和睦，优劣得所。

亲贤臣，远小人，此先汉所以兴隆也；亲小人，远贤臣，此后汉所以倾颓也。先帝在时，每与臣论此事，未尝不叹息痛恨于桓、灵也。侍中、尚书、长史、参军，此悉贞良死节之臣，愿陛下亲之信之，则汉室之隆，可计日而待也。

臣本布衣，躬耕于南阳，苟全性命于乱世，不求闻达于诸侯。先帝不以臣卑鄙，猥自枉屈，三顾臣于草庐之中，咨臣以当世之事，由是感激，遂许先帝以驱驰。后值倾覆，受任于败军之际，奉命于危难之间，尔来二十有一年矣。

先帝知臣谨慎，故临崩寄臣以大事也。受命以来，夙夜忧叹，恐托付不效，以伤先帝之明，故五月渡泸，深入不毛。今南方已定，兵甲已足，当奖率三军，北定中原，庶竭驽钝，攘除奸凶，兴复汉室，还于旧都。此臣所以报先帝而忠陛下之职分也。至于斟酌损益，进尽忠言，则攸之、祎、允之任也。

愿陛下托臣以讨贼兴复之效，不效，则治臣之罪，以告先帝之灵。若无兴德之言，则责攸之、祎、允等之慢，以彰其咎；陛下亦宜自谋，以咨诹善道，察纳雅言，深追先帝遗诏，臣不胜受恩感激。

今当远离，临表涕零，不知所言。"""
]


print("我来测试大杯了～")
testALL(prompts = prompts, models = models_venti)

print("="*30)
print("我来测试中杯了～")
testALL(prompts = prompts, models = models_grande)

print("="*30)
print("我来测试小杯了～")
testALL(prompts = prompts, models = models_tall)