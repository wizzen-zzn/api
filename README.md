1.首先安装必要的依赖：pip install requests
2.config.ini文件用于存储 API 密钥等敏感信息
用户需要自行替换其中的 your_api_key_here （从https://bailian.console.aliyun.com/?tab=model#/api-key获取自己的api key）
3.运行 qianwen_api.py 即可测试 API 调用
4.可以修改主函数中的 prompt 来发送不同的请求
5. 创建虚拟环境
conda env create -f environment.yml
6.激活虚拟环境
activate python313-env
7. 退出虚拟环境conda deactivate
