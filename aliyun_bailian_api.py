import requests
import json
import configparser
import os

class QianwenAPI:
    def __init__(self, config_file='config.ini'):
        """初始化通义千问API客户端
        
        Args:
            config_file: 配置文件路径，默认为'config.ini'
        """
        self.config = self.load_config(config_file)
        self.api_key = self.config.get('API', 'api_key', fallback=None)
        self.api_secret = self.config.get('API', 'api_secret', fallback=None)
        self.api_endpoint = self.config.get('API', 'endpoint', 
                                         fallback='https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation')
        
        # 验证必要的配置项
        if not all([self.api_key, self.api_secret]):
            raise ValueError("请在配置文件中正确设置api_key和api_secret")

    def load_config(self, config_file):
        """加载配置文件
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            配置解析器对象
        """
        if not os.path.exists(config_file):
            self.create_default_config(config_file)
            
        config = configparser.ConfigParser()
        config.read(config_file)
        return config

    def create_default_config(self, config_file):
        """创建默认配置文件
        
        Args:
            config_file: 配置文件路径
        """
        config = configparser.ConfigParser()
        config['API'] = {
            'api_key': 'your_api_key_here',
            'api_secret': 'your_api_secret_here',
            'endpoint': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
        }
        
        with open(config_file, 'w') as f:
            config.write(f)
        print(f"已创建默认配置文件: {config_file}")
        print("请编辑该文件，填入您的API密钥信息")

    def generate(self, prompt, model='qwen-turbo', temperature=0.7, max_tokens=1024):
        """调用通义千问API生成文本
        
        Args:
            prompt: 提示词
            model: 模型名称，默认为'qwen-turbo'
            temperature: 生成温度，控制随机性，0-1之间
            max_tokens: 最大生成token数
            
        Returns:
            API返回的响应结果
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        payload = {
            'model': model,
            'input': {
                'prompt': prompt
            },
            'parameters': {
                'temperature': temperature,
                'max_tokens': max_tokens
            }
        }
        
        try:
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                data=json.dumps(payload)
            )
            
            # 检查响应状态码
            response.raise_for_status()
            
            # 解析JSON响应
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    print(f"错误详情: {json.dumps(error_details, indent=2)}")
                except:
                    print(f"响应内容: {e.response.text}")
            return None

    def print_result(self, result):
        """格式化并打印API返回结果
        
        Args:
            result: API返回的结果字典
        """
        if not result:
            print("没有返回结果")
            return
            
        if 'output' in result and 'text' in result['output']:
            print("\n===== 生成结果 =====")
            print(result['output']['text'])
        else:
            print("\n===== API响应 =====")
            print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    try:
        # 初始化API客户端
        api = QianwenAPI()
        
        # 示例提示词
        prompt = "请简要介绍一下人工智能的发展历程"
        
        print(f"正在向通义千问发送请求: {prompt}")
        result = api.generate(prompt)
        
        # 打印结果
        api.print_result(result)
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
