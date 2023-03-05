import streamlit as st 
import openai 
import difflib
import re

def compare_texts(text1, text2):
    # 按单词拆分文本
    words1 = re.findall(r"\b\w+'\w+\b|\b\w+\b", text1)
    words2 = re.findall(r"\b\w+'\w+\b|\b\w+\b", text2)
    # 检查单词数量是否一致，不一致则添加空白单词
    if len(words1) < len(words2):
        words1 += [''] * (len(words2) - len(words1))
    elif len(words1) > len(words2):
        words2 += [''] * (len(words1) - len(words2))
    # 使用 difflib 库比较单词差异
    diff = difflib.ndiff(words1, words2)
    # 将差异标记为 markdown 语法
    result = []
    # print(''.join(diff).strip())
    i = 0
    for line in diff:        # 如果line不是空白行
        if line.startswith('-'):
            result.append(f":red[~~{line[2:]}~~] ")
        elif line.startswith('+'):
            result.append(f":blue[{line[2:]}] ")
        else:
            result.append(f"{line[2:]} ")
    # 将结果合并为一个字符串并返回
    result =''.join(result).strip()
    # 去掉++,--的情况
    # result = re.sub(r"\+ |\- ", "", result)
    return ''.join(result).strip()


st.title("Grammalyze语法检查装置")
col0,_=st.columns([1,1])
openai_api_key=col0.text_input("请输入OpenAI API Key",type="password")
col1,col2=st.columns(2)
input_text=col1.text_area("请输入文本",height=250)
output_text_area=col2.empty()
run_button=st.button("Grammalyze 语法检查")
openai.api_key=openai_api_key 
if run_button:
    prompt1="Please assist me with proofreading \
        and editing the following text for \
        proper grammar, fluency, and authenticity. \
        Please reply with the revised text only and \
        refrain from using quotation marks \
        to indicate the changes.\n\n"
    
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
        "role": "user",
        "content": prompt1+input_text,
        }
        ])
    output_text = (completion["choices"][0].get("message")
                .get("content").encode("utf8").decode())
    # 删除output_text前导的换行
    output_text = re.sub(r"^\n", "", output_text)
    output_text_area=col2.text_area("修订后",value=output_text,height=250)
    # 本来想PUA GPT出一个修订后的对比，但是没搞定，只能用difflib库来做
    # prompt2="""
    # Please compare the following two paragraphs and mark the differences using markdown syntax. 
    # For example:
    # This are a test.
    # This is a test.
    # The marked result should be:
    # This ~~are~~**is** a test.
    # Please reply with the marked result text only.
    # """
    # completion = openai.ChatCompletion.create(
    # model="gpt-3.5-turbo",
    # messages=[
    #     {
    #     "role": "user",
    #     "content": prompt2+f"{input_text}\n\n{output_text}",
    #     }
    #     ])
    # t_text2 = (completion["choices"][0].get("message")
    #             .get("content").encode("utf8").decode())
    # print("this is proofreading process:")
    # print(t_text2)
    st.write("修订前后对比：")
# 对比修订前后的文本
    
    st.markdown(compare_texts(input_text, output_text))
    with st.spinner("分析修订理由"):
        prompt3=f"Please indicate the reason for each modification, and translate reasons to Chinese.\n\nbefore:\n{input_text}\n\nafter]n{output_text}"
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                "role": "user",
                "content": prompt3,
                }
                ])
        t_text3 = (completion["choices"][0].get("message")
                    .get("content").encode("utf8").decode())
        st.write(t_text3)