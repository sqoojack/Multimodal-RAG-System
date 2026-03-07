# Dockerfile

# 使用 Python 3.11 作為基底映像檔，因為 Streamlit 專案需要 Python 環境
FROM python:3.11-slim

# 設定環境變數，讓 Python 不要產生 .pyc 檔案，加快速度
ENV PYTHONDONTWRITEBYTECODE 1
# 設定 Python 輸出不會被緩衝，讓 Streamlit Log 實時顯示
ENV PYTHONUNBUFFERED 1

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
# 由於您的 requirements.txt 包含 PyPDF2, Pillow, langchain 等
COPY requirements.txt .

RUN apt-get update \
    && apt-get install -y \
        tesseract-ocr \
        libtesseract-dev \
        ffmpeg \
        # 為了 Word docx/ppt 處理
        libxml2-dev \
        libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有應用程式檔案到容器
# 確保 config.py, app.py, utils.py 等都在 app 目錄下
COPY . .

# 由於 Streamlit 預設運行在 8501 端口
EXPOSE 8502

# 定義容器啟動時執行的指令
# CMD ["streamlit", "run", "app.py"]

CMD ["python", "-m", "streamlit", "run", "app.py"]