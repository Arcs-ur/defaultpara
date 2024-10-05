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

# 获取网页内容
# url = "https://docs.python.org/3/library/functions.html"
#url = "https://docs.python.org/3/library/os.path.html#module-os.path"
#url = "https://docs.python.org/3/library/sys.html#module-sys"
#url = "https://docs.python.org/3/library/math.html#module-math"
#url = "https://docs.python.org/3/library/datetime.html#module-datetime"
#url = "https://docs.python.org/3/library/random.html#module-random"
url = "https://docs.python.org/3/library/threading.html#module-threading"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# 找到所有函数的定义
functions = soup.find_all('dl')

# 存储结果
results = []

# 遍历每个函数定义
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
    for param in param_list:
        if '=' in param:
           default_params.append(param.strip())
    # 构建结果字典
    result = {
        "function_name": func_name,
        "all_parameters": params,
        "default_parameters": default_params
    }
    results.append(result)

# 写入到 JSON 文件
with open('builtin_module_threading.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("结果已写入文件中。")