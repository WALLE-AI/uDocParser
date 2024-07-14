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