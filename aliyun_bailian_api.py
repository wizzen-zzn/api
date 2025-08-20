import requests
import json
import time
import hmac
import hashlib
import base64
from urllib.parse import urlparse
import configparser

def load_config(config_file='config.ini'):
    """加载配置文件"""
    config = configparser.ConfigParser()
    config.read(config_file)
    return {
        'access_key': config.get('credentials', 'access_key'),
        'secret_key': config.get('credentials', 'secret_key'),
        'region_id': config.get('api', 'region_id'),
        'endpoint': config.get('api', 'endpoint'),
        'model': config.get('api', 'model')
    }

def generate_signature(access_key_secret, string_to_sign):
    """生成签名"""
    h = hmac.new(access_key_secret.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha1)
    return base64.b64encode(h.digest()).decode('utf-8')

def build_request_headers(config, payload):
    """构建请求头"""
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    nonce = str(int(time.time() * 1000))
    
    # 构建待签名字符串
    parsed_url = urlparse(config['endpoint'])
    host = parsed_url.netloc
    
    content_md5 = base64.b64encode(hashlib.md5(json.dumps(payload).encode('utf-8')).digest()).decode('utf-8')
    
    string_to_sign = (
        "POST\n"
        f"{content_md5}\n"
        "application/json\n"
        f"{timestamp}\n"
        f"host:{host}\n"
        "/"
    )
    
    # 生成签名
    signature = generate_signature(config['secret_key'], string_to_sign)
    
    # 构建Authorization
    authorization = f"acs {config['access_key']}:{signature}"
    
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Date": timestamp,
        "Host": host,
        "Authorization": authorization,
        "x-acs-signature-nonce": nonce
    }
    
    return headers

def call_bailian_api(config, prompt):
    """调用阿里云百炼API"""
    # 构建请求体
    payload = {
        "model": config['model'],
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 1024
    }
    
    # 构建请求头
    headers = build_request_headers(config, payload)
    
    try:
        # 发送请求
        response = requests.post(
            config['endpoint'],
            headers=headers,
            data=json.dumps(payload)
        )
        
        # 检查响应状态
        response.raise_for_status()
        
        # 返回解析后的响应
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"API请求出错: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"响应内容: {e.response.text}")
        return None

def main():
    """主函数"""
    try:
        # 加载配置
        config = load_config()
        print("配置加载成功")
        
        # 示例提问
        prompt = "请简要介绍一下人工智能的发展历程"
        print(f"发送请求: {prompt}")
        
        # 调用API
        result = call_bailian_api(config, prompt)
        
        # 打印结果
        if result:
            print("\nAPI返回结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 提取并打印回答内容
            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content']
                print("\n模型回答:")
                print(answer)
                
    except Exception as e:
        print(f"程序出错: {e}")

if __name__ == "__main__":
    main()
