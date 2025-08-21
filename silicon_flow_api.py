import requests
import configparser
import json

class SiliconFlowAPI:
    def __init__(self, config_file='config.ini'):
        """初始化API客户端，从配置文件加载密钥"""
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # 从配置文件获取API密钥
        self.api_key = self.config.get('siliconflow', 'api_key', fallback=None)
        if not self.api_key:
            raise ValueError("未在配置文件中找到有效的API密钥，请检查config.ini文件")
        
        # 硅基流动API端点
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        
        # 默认请求头
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate_response(self, prompt, model="silicon-1-turbo", temperature=0.7, max_tokens=1024):
        """
        调用硅基流动API生成响应
        
        try:
            # 构建请求数据
            payload = {
                "model": gpt-3.5-turbo,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # 发送POST请求
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应内容
            result = response.json()
            
            # 提取生成的文本
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return f"API返回格式异常: {json.dumps(result, indent=2)}"
                
        except requests.exceptions.HTTPError as e:
            return f"HTTP请求错误: {str(e)}\n错误详情: {json.dumps(response.json(), indent=2)}"
        except requests.exceptions.RequestException as e:
            return f"请求发生错误: {str(e)}"
        except Exception as e:
            return f"处理响应时发生错误: {str(e)}"

if __name__ == "__main__":
    try:
        # 初始化API客户端
        api_client = SiliconFlowAPI()
        
        # 测试提示词
        test_prompt = "请简要介绍一下硅基流动大模型的特点"
        
        # 调用API
        print("正在向硅基流动API发送请求...")
        response = api_client.generate_response(test_prompt)
        
        # 打印结果
        print("\n===== 模型响应 =====")
        print(response)
        
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
