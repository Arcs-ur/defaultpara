import json
import os
import re

def parse_value(val_str):
    """将字符串值安全转换为 Python 对象（支持数字、None、字符串等）"""
    val_str = val_str.strip()
    if val_str in ("<no_default>", "<NA>", "N/A", "NA"):
        return None, False
    if val_str == "None":
        return None, True
    try:
        value = eval(val_str, {"__builtins__": {}}, {})
        # 如果是 bytes 类型，转成字符串
        if isinstance(value, bytes):
            return val_str, True  # 保留原始字符串形式
        return value, True
    except Exception:
        return val_str, True  # fallback 成字符串


def process_json_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = {}
    count = 0

    for item in data:
        func_full = item["function_name"].strip().rstrip("¶")  # 去掉换行标记
        func_base = func_full.split("(", 1)[0]

        for param_str in item.get("default_parameters", []):
            if "=" not in param_str:
                continue
            param, raw_value = param_str.split("=", 1)
            param = param.strip()
            value, valid = parse_value(raw_value)
            if not valid:
                continue
            key = f"{func_base}.{param}"
            result[key] = {
                "funcname": func_base,
                "param": param,
                "value": value
            }
            count += 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"处理完成：共提取 {count} 条配置项。输出文件：{output_path}")

if __name__ == "__main__":
    input_file = "defaultpara_pandas_py/pandas.json"   # 替换成你的输入文件路径
    output_file = "SPT/SPT_pd.json"
    process_json_file(input_file, output_file)
