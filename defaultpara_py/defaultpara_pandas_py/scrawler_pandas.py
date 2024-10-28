import requests
from bs4 import BeautifulSoup
import json
import re

def extract_parameters(func_string):
    # 正则表达式匹配括号内的内容
    match = re.search(r'\((.*?)\)', func_string)
    if match:
        return match.group(1)  # 返回括号内的内容
    return None

# NumPy 函数类页面
base_url = "https://pandas.pydata.org/docs/reference/index.html"

# 发送请求并获取页面内容
response = requests.get(base_url)
soup = BeautifulSoup(response.content, 'html.parser')

# 找到所有函数类链接
function_class_links = []
#这里的>是css选择器的子代选择器，表示选择div下的ul下的li标签
for link in soup.select('div.toctree-wrapper.compound > ul > li > a.reference.internal'):
    href = link.get('href')
    #print(href)
    if href:
        function_class_links.append(f"https://pandas.pydata.org/docs/reference/{href}")

function_definitions = {}
results = []
# 遍历每个函数类链接，爬取函数定义链接
for class_link in function_class_links:
    try:
        class_response = requests.get(class_link)
        class_soup = BeautifulSoup(class_response.text, 'html.parser')
        # 找到所有函数的链接
        function_links = class_soup.select('a.reference.internal')  # 更新选择器
        for link in function_links:
            function_href = link.get('href')
            #print(function_href)
            if function_href:
                
                function_url = f"https://pandas.pydata.org/docs/reference/{function_href}"
                
                # 访问函数定义页面
                function_response = requests.get(function_url)
                function_soup = BeautifulSoup(function_response.content, 'html.parser')
                functions = function_soup.find_all('dl')
                # 提取函数名称
                for function in functions:
                    func_name = function.find('dt').get_text(strip=True)
                    params = extract_parameters(func_name)
                    default_params = []
                    # 寻找默认参数
                    if params is None:
                        continue
                    if params == '':
                        continue
                    param_list = params.split(',')
                    dftpara_exist = False
                    for param in param_list:
                        if '=' in param:
                            dftpara_exist = True
                            default_params.append(param.strip())
    # 构建结果字典
                    if dftpara_exist:
                        result = {
                            "function_name": func_name,
                            "all_parameters": params,
                            "default_parameters": default_params
                        }
                        results.append(result)
                        print(result)
        function_definitions[class_link] = result
        print(f"已处理 {class_link}")
    except Exception as e:
        print(f"处理 {class_link} 时出现错误: {e}")

# 将结果写入 numpy.json 文件
with open('pandas.json', 'w', encoding='utf-8') as json_file:
    json.dump(results, json_file, ensure_ascii=False, indent=4)

print("函数定义已成功写入 pandas.json 文件。")