import fitz  # PyMuPDF
import os
import pytesseract
from PIL import Image
import json
import re

class PDFPlugin():
    def __init__(self, path, store_path,filename):
        self.pdf_path = path + '/' + filename
        self.store_path = store_path
        self.page_num = 0
        self.text = '' # PDF文本
        self.filename=filename

        if not os.path.exists(store_path):
            os.mkdir(store_path)

    def remove_references_bibliography(self,text):
    # 检查 "References" 是否在文本中
        if "References" in text:
        # 分割文本，并只保留第一个部分（即 "References" 之前的部分）
            text = text.split("References")[0]
    # 检查 "Bibliography" 是否在文本中
        if "Bibliography" in text:
            text = text.split("Bibliography")[0]
        # return text
        if "REFERENCES" in text:
            text = text.split("REFERENCES")[0]
        # return text
        if "BIBLIOGRAPHY" in text:
            text = text.split("BIBLIOGRAPHY")[0]
        return text

    def remove_latexit_blocks(self,text):
        """
     Removes blocks of text starting with a line containing "<latexit" and
     ending with a line containing "</latexit>", including these lines.
    
     Parameters:
     - text: str, the input text containing the blocks to be removed.
    
     Returns:
     - The modified text with the specified blocks removed.
        """
    
        lines = text.split('\n')

        modified_lines = []

        inside_block = False

        for line in lines:
        # Check if we're entering a <latexit block
            if "<latexit" in line:
                inside_block = True
                continue  
            if "</latexit>" in line:
                inside_block = False
                continue  
            if not inside_block:
                modified_lines.append(line)
    
    # Join the modified lines back into a single string
        modified_text = '\n'.join(modified_lines)
    
        return modified_text
        
    def extract_text(self):
        """
        从PDF中提取全文文本
        """
        pdf_path = self.pdf_path
        doc = fitz.open(pdf_path)
        self.page_num = len(doc)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]

        for page_num in range(len(doc)):
            page = doc[page_num]
            # 获取每页的文本
            page_text = page.get_text()
            if "References" in page_text or "Bibliography" in page_text or "REFERENCES" in page_text or "BIBLIOGRAPHY" in page_text:
                page_text = self.remove_references_bibliography(page_text)
                self.text += page_text
                break 
            self.text += page_text
        self.text=self.remove_latexit_blocks(self.text)
        text_path = os.path.join(self.store_path, self.filename.replace('.pdf', '.txt'))
        with open(text_path, 'w', encoding='utf-8-sig') as f:
            f.write(self.text)
        doc.close()

    def get_text(self):
        return self.text
        

if __name__ == '__main__':
    # # 用pdfplugin
    folder_path = 'pdf'
    pdf_filenames = []
    # 遍历指定文件夹中的所有文件和文件夹
    for filename in os.listdir(folder_path):
        # 检查文件名是否以 ".pdf" 结尾
        if filename.lower().endswith('.pdf'):
            pdf_filenames.append(filename)
    store_path = 'text'
    for filename in pdf_filenames:
        pdf = PDFPlugin(folder_path, store_path, filename)
        pdf.extract_text()


