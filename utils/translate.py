# utils/translate.py
import requests

def translate_text(text: str) -> str:
    if not text:
        return ""
        
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    json_data = {
        "content": text,
        "targetLanguageCode": "zh-Hans"
    }
    
    try:
        response = requests.post('https://www.tranlis.com/api/trans/translation/translateText', headers=headers, json=json_data, timeout=10)
        if response.status_code == 200:
            return response.json().get("data", {}).get("translatedText", "")
    except Exception as e:
        print(f"翻译错误: {e}")
        return ""
        
    return ""