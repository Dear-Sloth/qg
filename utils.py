import tiktoken, json
from functools import lru_cache

def chat_with_gpt(client, prompt, max_tokens, n):
    # 用GPT生成QA对
    #print(prompt)
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=prompt,
        n = n,
        # max_tokens = 2048,
        max_tokens = max_tokens,
        temperature = 0.2,
        top_p=0.95,
    )
    
    content_str = completion.choices[0].message.content
    if 'questions_and_answers' in content_str:
        content = json.loads(content_str)
        return str(content['questions_and_answers']).strip('[]')
    else:
        return content_str


class LazyloadTiktoken(object):
    def __init__(self, model):
        self.model = model

    @staticmethod
    @lru_cache(maxsize=128)
    def get_encoder(model):
        print('正在加载tokenizer，如果是第一次运行，可能需要一点时间下载参数')
        tmp = tiktoken.encoding_for_model(model)
        print('加载tokenizer完毕')
        return tmp
    
    def encode(self, *args, **kwargs):
        encoder = self.get_encoder(self.model) 
        return encoder.encode(*args, **kwargs)
    
    def decode(self, *args, **kwargs):
        encoder = self.get_encoder(self.model) 
        return encoder.decode(*args, **kwargs)

tokenizer_gpt4 = LazyloadTiktoken("gpt-4")  