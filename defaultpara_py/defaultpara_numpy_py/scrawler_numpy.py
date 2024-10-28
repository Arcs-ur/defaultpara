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
base_url = "https://numpy.org/doc/stable/reference/routines.html"

# 发送请求并获取页面内容
response = requests.get(base_url)
soup = BeautifulSoup(response.text, 'html.parser')

# 找到所有函数类链接
function_class_links = []
for li in soup.select('#routines-and-objects-by-topic > div.toctree-wrapper.compound > ul > li'):
    link = li.find('a')
    if link:
        href = link.get('href')
        if href:
            #print(f"https://numpy.org/doc/stable/reference/{href}")
            function_class_links.append(f"https://numpy.org/doc/stable/reference/{href}")

# 存储函数定义
#function_class_links = ['https://numpy.org/doc/stable/reference/routines.array-creation.html', 'https://numpy.org/doc/stable/reference/routines.array-manipulation.html', 'https://numpy.org/doc/stable/reference/routines.bitwise.html', 'https://numpy.org/doc/stable/reference/routines.strings.html', 'https://numpy.org/doc/stable/reference/routines.datetime.html', 'https://numpy.org/doc/stable/reference/routines.dtype.html', 'https://numpy.org/doc/stable/reference/routines.emath.html', 'https://numpy.org/doc/stable/reference/routines.err.html', 'https://numpy.org/doc/stable/reference/routines.exceptions.html', 'https://numpy.org/doc/stable/reference/routines.fft.html', 'https://numpy.org/doc/stable/reference/routines.functional.html', 'https://numpy.org/doc/stable/reference/routines.io.html', 'https://numpy.org/doc/stable/reference/routines.indexing.html', 'https://numpy.org/doc/stable/reference/routines.linalg.html', 'https://numpy.org/doc/stable/reference/routines.logic.html', 'https://numpy.org/doc/stable/reference/routines.ma.html', 'https://numpy.org/doc/stable/reference/routines.math.html', 'https://numpy.org/doc/stable/reference/routines.other.html', 'https://numpy.org/doc/stable/reference/routines.polynomials.html', 'https://numpy.org/doc/stable/reference/random/index.html', 'https://numpy.org/doc/stable/reference/routines.set.html', 'https://numpy.org/doc/stable/reference/routines.sort.html', 'https://numpy.org/doc/stable/reference/routines.statistics.html', 'https://numpy.org/doc/stable/reference/routines.testing.html', 'https://numpy.org/doc/stable/reference/routines.window.html']
function_definitions = {}
results = []
#print(function_class_links)
# 遍历每个函数类链接，爬取函数定义链接
for class_link in function_class_links:
    try:
        class_response = requests.get(class_link)
        class_soup = BeautifulSoup(class_response.text, 'html.parser')

        # 找到所有函数的链接
        function_links = class_soup.select('a.reference.internal')  # 更新选择器

        for link in function_links:
            function_href = link.get('href')
            if function_href == 'module_structure.html':
                continue
            if function_href and function_href.startswith('generated'):
                function_url = f"https://numpy.org/doc/stable/reference/{function_href}"
                
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
                        print(results)

        function_definitions[class_link] = results
        print(function_definitions)
        print(f"已处理 {class_link}")
    except Exception as e:
        print(f"处理 {class_link} 时出现错误: {e}")

# 将结果写入 numpy.json 文件
with open('numpy.json', 'w', encoding='utf-8') as json_file:
    json.dump(results, json_file, ensure_ascii=False, indent=4)

print("函数定义已成功写入 numpy.json 文件。")