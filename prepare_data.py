import os
import streamlit as st
import subprocess
import pexpect

def run_command(command, answers):
    process = pexpect.spawn(command)
    process.expect("^\[.*\]$", timeout=None)  # 等待命令提示符出现
    for answer in answers:
        process.sendline(answer)
        process.expect("^\[.*\]$", timeout=None)  # 等待下一个问题出现
    output = process.read().decode()
    return output

# 其他代码保持不变

def main():
    # ...

    # 准备数据并生成 JSONL 文件
    if st.button("Prepare Data"):
        if uploaded_file is not None and api_key:
            # ...

            # 运行 CLI 命令
            command = f"OPENAI_API_KEY={api_key} openai tools fine_tunes.prepare_data -f {file_path}"
            
            # 自动回答所有问题
            answers = ["y"] * 5  # 回答5个问题都是 "y"
            output = run_command(command, answers)

            if not output:
                st.warning("An error occurred during data preparation")
            else:
                # 查找生成的 JSONL 文件
                jsonl_filename = None
                for filename in os.listdir(downloads_folder):
                    if filename.endswith(".jsonl"):
                        jsonl_filename = filename
                        break

                if jsonl_filename:
                    # 下载生成的 JSONL 文件
                    download_link = f"./downloads/{jsonl_filename}"
                    st.markdown(f"### [Download Prepared Data JSONL]({download_link})")
                else:
                    st.warning("Failed to find JSONL file")
        else:
            st.warning("Please upload an Excel file and enter your OpenAI API Key")

# 其他代码保持不变

if __name__ == "__main__":
    main()
