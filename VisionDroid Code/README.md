# LLM Test

使用 GPT-3.5 或者 Spark 星火大模型进行 App Testing

![structure](./assets/structure.png)

## 使用方法

找到 app 后，手动将 `cmd.py` 中的 `PACKAGE = "xxx"` 部分改成对应的包名

包名可以通过命令行运行 `adb shell dumpsys activity activities | grep mControlTarget=Window` 获得

如果是开源 app，同时将 `AndroidManifest.xml` 的内容换成源代码中 `/main/app/src/main/AndroidManifest.xml` 的内容

**注意程序每次运行前都会清空上一次的各种路径存储！！！请及时保存！！！**

## 网络代理

在 `GptModel.py` 中通过

```
import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10809'
```

设置了网络代理

### How to set up a proxy for OpenAI's API in Python?

https://github.com/Onelinerhub/onelinerhub/blob/main//python-openai/how-to-set-up-a-proxy-for-openai-s-api-in-python.md