import os
import streamlit as st
import subprocess

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)
    output_lines = []
    with st.expander("Terminal Output"):
        for line in process.stdout:
            output_lines.append(line.strip())
            st.text(line.strip())

    _, error = process.communicate()
    return output_lines, error

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
            output_lines, error = run_command(command)

            # 在终端输出中寻找需要用户回答的问题
            question_indices = [i for i, line in enumerate(output_lines) if line.endswith("[Y/n]:")]
            for index in question_indices:
                question = output_lines[index]
                default_answer = "Y" if question.endswith("[Y/n]:") else ""
                answer = st.radio(question, ("Yes", "No"), key=str(index), index=0)

            if not error:
                # 解析 CLI 输出并获取生成的 JSONL 文件名
                jsonl_filename = None
                for line in output_lines:
                    if line.startswith("Wrote modified files to"):
                        jsonl_filename = line.split()[-1]
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
