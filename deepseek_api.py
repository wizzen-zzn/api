import configparser
import requests
import json

class DeepSeekAPI:
    def __init__(self, config_file='config.ini'):
        """初始化DeepSeek API客户端"""
        # 加载配置文件
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # 获取API密钥
        try:
            self.api_key = self.config.get('deepseek', 'api_key')
            if not self.api_key or self.api_key == 'your_deepseek_api_key_here':
                raise ValueError("请在config.ini中配置有效的DeepSeek API密钥")
        except (configparser.NoSectionError, configparser.NoOptionError):
            raise ValueError("配置文件格式错误，请检查config.ini是否包含[deepseek]部分和api_key选项")
        
        # API端点
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
        # 支持的模型列表
        self.supported_models = [
            "deepseek-chat",
            "deepseek-vl",
            "deepseek-coder",
            "deepseek-r1"
        ]

    def generate_response(self, prompt, model="deepseek-chat", temperature=0.7, max_tokens=1024):
       
        # 检查模型是否支持
        if model not in self.supported_models:
            raise ValueError(f"不支持的模型: {model}，支持的模型有: {self.supported_models}")
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 构建请求体
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload)
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 提取并返回生成的内容
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return f"API返回格式异常: {json.dumps(result, indent=2)}"
                
        except requests.exceptions.HTTPError as e:
            # 处理HTTP错误
            try:
                error_details = response.json()
                error_msg = f"HTTP请求错误: {str(e)}\n错误详情: {json.dumps(error_details, indent=2)}"
            except:
                error_msg = f"HTTP请求错误: {str(e)}"
            raise Exception(error_msg)
        except Exception as e:
            # 处理其他错误
            raise Exception(f"调用API时发生错误: {str(e)}")

if __name__ == "__main__":
    try:
        # 初始化API客户端
        deepseek = DeepSeekAPI()
        
        # 测试提示词
        test_prompt = "请简要介绍一下DeepSeek大模型的特点"
        
        # 调用API
        print("正在向DeepSeek API发送请求...")
        response = deepseek.generate_response(
            prompt=test_prompt,
            model="deepseek-chat",
            temperature=0.5,
            max_tokens=500
        )
        
        # 打印结果
        print("\n===== 模型响应 =====")
        print(response)
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
