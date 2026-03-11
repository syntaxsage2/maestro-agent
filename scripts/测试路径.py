import os

# 获取当前脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 拼接相对路径
file_path = os.path.join(script_dir, "data", "knowledge", "sample_docs.txt")

print(script_dir,"\n")
print(file_path)