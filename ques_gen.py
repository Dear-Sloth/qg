import os
import openai
from utils import tokenizer_gpt4, chat_with_gpt
import json

#os.environ["OPENAI_API_KEY"] = "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"
os.environ["AZURE_OPENAI_KEY"] = "cda7b35e13ac4b34b0ceabbb5445d8b5"
os.environ["AZURE_OPENAI_ENDPOINT"]="https://zenithae.openai.azure.com/"
openai.api_key = os.environ["AZURE_OPENAI_KEY"]
openai.api_base = os.environ["AZURE_OPENAI_ENDPOINT"]
openai.api_type = 'azure'
openai.api_version = '2023-07-01-preview'
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'



def get_token_num(text):
    # 计算文本的token数量
    return len(tokenizer_gpt4.encode(text))

class TextQA:
    def __init__(self, text_file, qa_file, n, max_input_tokens=7000):
        self.client = openai
        self.text_file = text_file
        self.qa_file = qa_file
        self.n = n #每次生成的QA对数量
        self.max_input_tokens = max_input_tokens

    def read_text(self):
        with open(self.text_file, 'r', encoding='utf-8') as file:
            return file.read()

    def split_text(self, text, max_length):
        words = text.split(' ')
        current_length = 0
        parts = []
        current_part = []

        for word in words:
            # 检查参考文献关键词
            if "References" in word or "Bibliography" in word or "BIBLIOGRAPHY" in word or "REFERENCES" in word:
                # 如果发现参考文献关键词，添加当前部分并停止
                if current_part:
                    parts.append(' '.join(current_part))
                break

            current_length += get_token_num(word + ' ')  # 加上空格的token
            if current_length > max_length:
                parts.append(' '.join(current_part))
                current_part = [word]
                current_length = get_token_num(word)
            else:
                current_part.append(word)

        # 添加最后一部分，如果没有遇到参考文献关键词
        if current_part and not ("References" in current_part[-1] or "Bibliography" in current_part[-1] or "REFERENCES" in current_part[-1] or "BIBLIOGRAPHY" in current_part[-1]):
            parts.append(' '.join(current_part))

        return parts

    def generate_questions(self, text):
        """生成基于文本的五个问题"""
        prompt = [
                {
                 "role": "system",
                 "content": "You are a helpful assistant tasked with proposing high quality questions based on given academic papers."
                },
                {
                   "role": "user",
                   "content": f"\
Please read and understand the following paper content in detail, and first briefly analyze and determine the style of the paper (such as theoretical research, experimental research, review, etc.). Based on the determined style, your task is to analyze the structure and content of the paper in depth and then ask 20 questions. Please follow these guidelines to ensure quality and diversity of questions:\
\
Essay style and type analysis:\
- [Here is a brief analysis of the style and type of the paper]\
\
###\
\
Next, please ask 20 English questions after in-depth analysis based on the content of the paper, covering the following aspects. Please directly output 1-20 questions in a row without writing categories or making any comments:\
\
**Theoretical and basic knowledge understanding** (5 questions):\
    - In-depth discussion of the basic theory, core concepts and research purpose of the paper. For example, what problem does the research aim to solve? What is the research background and theoretical basis?\
\
**Methodological In-depth** (5 questions):\
    - Ask in detail about the research methods, experimental design, data collection and analysis process of the paper. For example, what methods did the study use to collect data? What are the selection criteria for these methods?\
\
**Result Analysis** (5 questions):\
    - Focus on the paper's main findings, data interpretation, and conclusions. For example, what key information did the experimental results reveal? How does the author draw conclusions based on the results?\
\
**Simplified Critical and Creative Thinking** (5 questions):\
    - Optionally, ask one or two questions to assess the limitations of the study or propose novel thinking based on the findings. For example, what are the potential limitations of the study? How do the results of the paper inspire future research directions?\
\
Please ensure that the questions cover key aspects of the paper and encourage a deep understanding of the paper's content. Try to give the questions some depth to facilitate in-depth analysis of the detailed content of the paper.\
\
Here is the content of the paper:{text}"
                }
                ]

        response = chat_with_gpt(self.client, prompt, 8192 - self.max_input_tokens, self.n)
        return response

    def save_qa(self, qa):
        with open(self.qa_file, 'a', encoding='utf-8') as file:  # 使用 'a' 模式附加到文件
            file.write(qa + ',\n')

    def remove_line_breaks(self,text):
        lines = text.split('\n')  # 将文本分割为行
        result = []
        k=0
        result.append(lines[0].rstrip())
        for i in range(len(lines)):
        # 删除行尾的空白字符
            line = lines[i].rstrip()
            if i==0:
                continue
            elif not result[k].endswith(('.', ':')):
                result[k]=str(result[k])+' '+ str(line)
            else:
            # 否则保留当前行和其换行符
                result.append(line)
                k=k+1
        return '\n'.join(result)

    def ins_text(self,original,to_insert):
        substring='with each score being unique.'
        to_insert='\n Here is the text: \n' + to_insert
        first_index = original.find(substring)

        if first_index != -1:
             # 查找第一次出现的位置
            new_string = original[:first_index + len(substring)] + to_insert + original[first_index + len(substring):]
        else:
            new_string = original
        
        return new_string

    def process(self):
        text = self.read_text()
        # 分割文本，预留一半token给输出
        parts = self.split_text(text, self.max_input_tokens)  
        print(len(parts))
        for part in parts:
            part = self.remove_line_breaks(part)
            qa = self.generate_questions(part)
            # print(qa)
            qa = self.ins_text(qa,part)
            self.save_qa(qa)



if __name__ == '__main__':

    folder_path = 'text'
    txt_filenames = []
    store_path = 'jsonl'
    # 遍历指定文件夹中的所有文件和文件夹
    for filename in os.listdir(folder_path):
        # 检查文件名是否以 ".txt" 结尾
        if filename.lower().endswith('.txt'):
            txt_filenames.append(filename)

    for filename in txt_filenames:
        text_file = './'+folder_path+'/'+filename
        qa_file = './'+store_path+'/'+filename.replace('.txt', '.jsonl')
        textqa = TextQA(text_file, qa_file, 1, 7000)
        textqa.process()
