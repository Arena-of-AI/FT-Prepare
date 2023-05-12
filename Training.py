import os
import streamlit as st
import subprocess

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode(), error.decode()

def main():
    # 创建 "temp" 文件夹
    if not os.path.exists("temp"):
        os.makedirs("temp")

    # 创建 "downloads" 文件夹
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    st.title("Data Preparation Tool")

    # 上传 Excel 文件
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    if uploaded_file is not None:
        # 显示上传的文件名
        st.write("Uploaded file:", uploaded_file.name)

    # 准备数据并生成 JSONL 文件
    if st.button("Prepare Data"):
        if uploaded_file is not None:
            # 保存上传的 Excel 文件
            file_path = f"temp/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 运行 CLI 命令
            command = f"openai tools fine_tunes.prepare_data -f {file_path}"
            output, error = run_command(command)

            # 将输出写入临时文件
            output_file = "temp/prepared_data.jsonl"
            with open(output_file, "w") as f:
                f.write(output)

            # 下载生成的 JSONL 文件
            st.markdown(f"### [Download Prepared Data JSONL](downloads/{output_file})")
        else:
            st.warning("Please upload an Excel file")

if __name__ == "__main__":
    main()
