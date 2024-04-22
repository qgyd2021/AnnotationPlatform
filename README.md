## 标注平台


```text
HTML 参考链接: 

https://www.runoob.com/html/html-tables.html

https://github.com/glefundes/audio-class
https://github.com/CrowdCurio/audio-annotator

https://www.runoob.com/sqlite/sqlite-python.html


http://10.75.27.247:9080/voicemail
http://127.0.0.1:9080/voicemail

```


```text

1. 新的未标注数据, 复制到目录: 
/data/tianxing/PycharmProjects/datasets/voicemail/zh-TW

2. 标注后, 将数据移动到目录: 
/data/tianxing/PycharmProjects/datasets/voicemail/zh-TW/wav_finished

3. 根据 wav_finished 训练模型.

4. 模型生成测评 excel. 

5. 根据测评 excel 向 sqlite 导入 `纠错任务`. 
音频文件和路径仍保存在原 wav_finished 目录中. 
建立 wav_finished 到 static 目录的软链接. 

6. 纠错任务标注后, 如与原来的标注不同, 则直接移动文件. 
移动后, 在 sqlite 中更新该文件的新的目录, 并标识 checked. 

```

### 备注
创建软链接
```text
ln -s /data/tianxing/PycharmProjects/datasets/voicemail/EarlyMedia-1 EarlyMedia-1
```
