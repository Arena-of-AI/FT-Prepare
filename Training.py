import os
import streamlit as st
import subprocess

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode(), error.decode()

def create_temp_folder():
    # 创建 "temp" 文件夹
    temp_folder = os.path.join(os.getcwd(), "temp")
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    return temp_folder

def create_downloads_folder():
    # 创建 "downloads" 文件夹
    downloads_folder = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)
    return downloads_folder

def download_file(file_path):
    with open(file_path, "rb") as file:
        file_data = file.read()
    st.download_button("Download Prepared Data JSONL", file_data, file_name="prepared_data.jsonl")

def main():
    st.title("Data Preparation Tool")

    temp_folder = create_temp_folder()
    downloads_folder = create_downloads_folder()

    # 上传 Excel 文件
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    if uploaded_file is not None:
        # 显示上传的文件名
        st.write("Uploaded file:", uploaded_file.name)

    # 准备数据并生成 JSONL 文件
    if st.button("Prepare Data"):
        if uploaded_file is not None:
            # 保存上传的 Excel 文件
            file_path = os.path.join(temp_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 运行 CLI 命令
            command = f"openai tools fine_tunes.prepare_data -f {file_path}"
            output, error = run_command(command)

            # 解析 CLI 输出并获取生成的 JSONL 文件名
            output_lines = output.split("\n")
            jsonl_filename = ""
            for line in output_lines:
                if line.startswith("Wrote modified files to"):
                    jsonl_filename = line.split("`")[1]
                    break

            if jsonl_filename:
                # 将生成的 JSONL 文件移动到 "downloads" 文件夹
                output_file = os.path.join(os.getcwd(), jsonl_filename)
                output_file_destination = os.path.join(downloads_folder, "prepared_data.jsonl")
                os.rename(output_file, output_file_destination)

                # 下载生成的 JSONL 文件
                download_file(output_file_destination)
            else:
                st.warning("Failed to generate JSONL file")
        else:
            st.warning("Please upload an Excel file")

if __name__ == "__main__":
    main()
