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
        if uploaded_file is not None and api_key:
            # 保存上传的 Excel 文件
            file_path = os.path.join(temp_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 运行 CLI 命令
            command = f"OPENAI_API_KEY={api_key} openai tools fine_tunes.prepare_data -f {file_path}"
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)

            # 显示终端输出和等待用户回答
            with st.expander("Terminal Output"):
                output_lines = []
                for line in process.stdout:
                    output_lines.append(line.strip())
                    st.text(line.strip())

                # 在终端输出中寻找需要用户回答的问题
                question_indices = [i for i, line in enumerate(output_lines) if line.startswith("[Recommended]") or line.startswith("[Required]")]
                for index in question_indices:
                    question = output_lines[index]
                    default_answer = "Y" if question.endswith("[Y/n]:") else ""
                    answer = st.text_input(question, default_answer)
                    process.stdin.write(answer + "\n")
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
                    download_file(os.path.join(downloads_folder, jsonl_filename))
                else:
                    st.warning("Failed to find JSONL file")
            else:
                st.warning("An error occurred during data preparation")
                st.error(error)
        else:
            st.warning("Please upload an Excel file and enter your OpenAI API Key")
