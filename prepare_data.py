import os
import streamlit as st
import subprocess

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)
    with st.expander("Terminal Output"):
        for line in process.stdout:
            st.text(line.strip())
    _, error = process.communicate()
    return error

def create_temp_folder():
    # 创建 "temp" 文件夹
    if not os.path.exists("temp"):
        os.makedirs("temp")
    return "temp"

def create_downloads_folder():
    # 创建 "downloads" 文件夹
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    return "downloads"

def main():
    st.title("Data Preparation Tool")

    # 输入 OpenAI API 密钥
    api_key = st.text_input("Enter OpenAI API Key")
    if not api_key:
        st.warning("Please enter your OpenAI API Key")

    temp_folder = create_temp_folder()
    downloads_folder = create_downloads_folder()

    # 上传 Excel 文件
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    if uploaded_file is not None:
        # 显示上传的文件名
        st.write("Uploaded file:", uploaded_file.name)

    # 准备数据并生成 JSONL 文件
    if st.button("Prepare Data"):
        if uploaded_file is not None and api_key:
            # 保存上传的 Excel 文件
            file_path = os.path.join(temp_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 运行 CLI 命令
            command = f"OPENAI_API_KEY={api_key} openai tools fine_tunes.prepare_data -f {file_path}"
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)

            # 自动回答所有问题
            with st.expander("Terminal Output"):
                while process.poll() is None:
                    line = process.stdout.readline().strip()
                    st.text(line)
                    if line.endswith("[Y/n]:"):
                        process.stdin.write("Y\n")
                        process.stdin.flush()

            _, error = process.communicate()

            if not error:
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
                st.warning("An error occurred during data preparation")
                st.error(error)
        else:
            st.warning("Please upload an Excel file and enter your OpenAI API Key")

if __name__ == "__main__":
    main()
