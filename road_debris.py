import requests
import json
import base64
import os
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

# 请替换为你的实际信息
API_KEY = ""  # 从阿里云控制台获取
API_ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1"
IMAGE_PATH = r""

# 英文提示词
DETECTION_PROMPT = """
You are a professional road surface debris detection assistant. Road debris refers to foreign objects that should not be present on road surfaces, including stones, construction waste, piles of sand/soil, plastic bags, cardboard boxes, branches, leaves, and similar items. Explicitly exclude vehicles, pedestrians, guardrails, streetlights, and other normal road elements.

Task: Detect all debris within the road area in the image. Return ONLY a JSON format result with no additional text.

If debris is detected, return: {"result": "yes", "bounding_boxes": [[xmin, ymin, xmax, ymax], ...]} where coordinates are in pixel units with the origin (0,0) at the top-left corner of the image.

If no debris is detected, return: {"result": "no"}
"""


# 调用千问VL模型（修复编码问题）
def get_debris_detection_result(image_path, prompt):
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误：图片文件不存在 - {image_path}")
        return None

    try:
        # 读取图片并转换为Base64（指定编码为utf-8）
        with open(image_path, "rb") as f:
            image_data = f.read()
        # 确保Base64编码使用utf-8格式
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        # 构造符合DashScope API要求的请求体
        payload = {
            "model": "qwen-plus",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt.encode('utf-8').decode('utf-8')},  # 确保文本编码正确
                            {"type": "image", "image": image_base64}
                        ]
                    }
                ]
            },
            "parameters": {
                "temperature": 0.01,
                "top_p": 0.9
            }
        }

        # 发送请求
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json; charset=utf-8",  # 明确指定utf-8编码
            "X-Dashscope-Region": "cn-beijing"
        }

        # 确保请求数据正确编码为utf-8
        response = requests.post(
            API_ENDPOINT,
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),  # 关键修复：显式编码为utf-8
            timeout=60
        )

        # 打印详细响应（用于调试）
        print("API响应状态码:", response.status_code)
        print("API响应内容:", response.text)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"HTTP错误: {e}")
        print("错误详情:", response.text)
    except UnicodeEncodeError as e:
        print(f"编码错误: {str(e)}")
        print("问题字符位置:", e.args[2], "问题字符:", repr(e.args[1][e.args[2]]))
    except Exception as e:
        print(f"请求失败: {str(e)}")
    return None


# 解析检测结果
def parse_bounding_boxes(detection_result):
    if not detection_result:
        return None

    try:
        content = detection_result["output"]["choices"][0]["message"]["content"]
        # 提取JSON部分
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start == -1 or json_end == 0:
            print("无法提取JSON结果")
            return None

        # 确保解码正确
        result_json = json.loads(content[json_start:json_end].encode('utf-8').decode('utf-8'))
        if result_json.get("result") == "yes":
            return result_json["bounding_boxes"]
        else:
            print("未检测到杂物")
            return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"结果解析错误: {str(e)}")
        return None


#画框功能
def draw_boxes_with_pillow(image_path, bounding_boxes, save_path="result_pillow.jpg"):
    if not bounding_boxes:
        return
    try:
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        box_color = (255, 0, 0)
        text_color = (255, 255, 255)

        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        for idx, (xmin, ymin, xmax, ymax) in enumerate(bounding_boxes, 1):
            draw.rectangle([xmin, ymin, xmax, ymax], outline=box_color, width=3)
            text = f"Debris {idx}"
            text_pos = (xmin + 5, ymin - 25 if ymin > 25 else ymin + 5)
            draw.text(text_pos, text, fill=text_color, font=font)

        image.save(save_path)
        print(f"Pillow结果已保存: {save_path}")
    except Exception as e:
        print(f"Pillow画框错误: {str(e)}")


def draw_boxes_with_opencv(image_path, bounding_boxes, save_path="result_opencv.jpg"):
    if not bounding_boxes:
        return
    try:
        image = cv2.imread(image_path)
        if image is None:
            print("无法读取图片")
            return

        box_color = (0, 0, 255)
        text_color = (255, 255, 255)

        for idx, (xmin, ymin, xmax, ymax) in enumerate(bounding_boxes, 1):
            cv2.rectangle(image, (int(xmin), int(ymin)), (int(xmax), int(ymax)), box_color, 3)
            text = f"Debris {idx}"
            text_pos = (int(xmin) + 5, int(ymin) - 10 if int(ymin) > 10 else int(ymin) + 20)
            cv2.putText(image, text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)

        cv2.imwrite(save_path, image)
        print(f"OpenCV结果已保存: {save_path}")
    except Exception as e:
        print(f"OpenCV画框错误: {str(e)}")



if __name__ == "__main__":
    detection_result = get_debris_detection_result(IMAGE_PATH, DETECTION_PROMPT)
    bounding_boxes = parse_bounding_boxes(detection_result)
    if bounding_boxes:
        draw_boxes_with_pillow(IMAGE_PATH, bounding_boxes)
        draw_boxes_with_opencv(IMAGE_PATH, bounding_boxes)
