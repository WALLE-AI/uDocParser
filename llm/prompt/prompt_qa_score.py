PROMPT_QA_SCORE = '''
There is an existing knowledge base chatbot application. 
I asked it a question and got a reply. Do you think this reply is a good answer to the question? 
Please rate this reply. 
The score is an integer between 0 and 10. 0 means that the reply cannot answer the question at all, and 10 means that the reply can answer the question perfectly

Question: Where is France and what is it’s capital?
Reply: France is in western Europe and Paris is its capital.

'''

PROMPT_SS_SIMILARITY_SCORE='''
你是一个资深的语言学家，能够高准确性的识别出两个句子的语义相似性，并且通过0-5打分，0为毫无相似性，5为高度相似，如下为用户输入两个句子
句子1：在回顾式心脏扫描数据采集的过程中，如果出现ECG信号异常，系统应支持利用采集到的数据完成图像重建
句子2：系统应支持用户在回顾式扫描模式下可编辑ECG波形并使用编辑后的ECG信号进行图像重建

请使用采用如下json格式进行输出,无需进行解释，直接输出结果即可：
{
    score:"xxx"
    similarity_evaluation:"xxxx"
}

'''

GENERATOR_QA_PROMPT = (
    '<Task> The user will send a long text. Generate a Question and Answer pairs only using the knowledge in the long text. Please think step by step.'
    'Step 1: Understand and summarize the main content of this text.\n'
    'Step 2: What key information or concepts are mentioned in this text?\n'
    'Step 3: Decompose or combine multiple pieces of information and concepts.\n'
    'Step 4: Generate questions and answers based on these key information and concepts.\n'
    '<Constraints> The questions should be clear and detailed, and the answers should be detailed and complete. '
    'You must answer in {language}, in a style that is clear and detailed in {language}. No language other than {language} should be used. \n'
    '<Format> Use the following format: Q1:\nA1:\nQ2:\nA2:...\n'
    '<QA Pairs>'
)

SUGGESTED_QUESTIONS_AFTER_ANSWER_INSTRUCTION_PROMPT = (
    "Please help me predict the three most likely questions that human would ask, "
    "and keeping each question under 20 characters.\n"
    "MAKE SURE your output is the SAME language as the Assistant's latest response(if the main response is written in Chinese, then the language of your output must be using Chinese.)!\n"
    "The output must be an array in JSON format following the specified schema:\n"
    "[\"question1\",\"question2\",\"question3\"]\n"
)