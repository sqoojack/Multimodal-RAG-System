
## Command line:
```pip install -r requirements.txt```


```streamlit run app.py```
If the streamlit environment is weird (not same as conda environment), can execute this:
```python -m streamlit run app.py```


### 用docker 執行
```
docker-compose up --build
連到以下網址:
http://140.113.24.231:8502
```

### 把容器關掉
```
docker-compose down
```


### 測試mp3, mp4檔案
1. 選擇mp3_mp4知識庫
2. 選擇gpt-oss:20b模型
3. 下prompt: 知識庫中有哪些AI相關的知識, 請幫我統整