import requests
import json
from django.conf import settings


def callQwenApi(prompt):
    """
    调用阿里云Qwen API获取回答
    """
    headers = {
        "Authorization": f"Bearer {settings.LLM_CONFIG['API_KEY']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.LLM_CONFIG["Model"],
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        },
        "parameters": {
            "result_format": "message"  # 返回消息格式
        }
    }

    try:
        response = requests.post(
            settings.LLM_CONFIG["API_URL"],
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        result = response.json()
        if 'output' in result and 'choices' in result['output']:
            return result['output']['choices'][0]['message']['content']
        elif 'output' in result and 'text' in result['output']:
            return result['output']['text']
        else:
            return "抱歉，无法解析API响应。"

    except requests.exceptions.HTTPError as err:
        print(f"HTTP错误: {err}")
        return f"API请求错误: {err}"
    except Exception as e:
        print(f"API调用失败: {str(e)}")
        return "抱歉，获取回答时出现问题，请稍后再试。"