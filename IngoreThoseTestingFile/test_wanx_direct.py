#!/usr/bin/env python3
"""
Direct test of Wanx API using curl-like approach.
"""

import requests
import json
import time

def test_wanx_direct():
    """Test Wanx API directly."""
    
    api_key = "sk-73c97dcb22834612990bad7f93639e8a"
    endpoint = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    
    payload = {
        "model": "wanx-v1",
        "input": {
            "prompt": "一个勇敢的太空探险家，穿着未来科技装备，站在外星球表面",
            "negative_prompt": "blurry, low quality",
            "style": "photography",
            "size": "1024*1024",
            "n": 1
        }
    }
    
    print("🚀 直接调用万相API...")
    print(f"📡 端点: {endpoint}")
    print(f"🔑 API密钥: {api_key[:10]}...")
    print(f"📝 载荷: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            
            if "output" in result and "task_id" in result["output"]:
                task_id = result["output"]["task_id"]
                print(f"✅ 任务创建成功，任务ID: {task_id}")
                
                # Query task status
                query_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
                query_headers = {
                    "Authorization": f"Bearer {api_key}"
                }
                
                print(f"🔍 查询任务状态: {query_url}")
                
                for i in range(10):  # Try 10 times
                    time.sleep(3)
                    
                    query_response = requests.get(query_url, headers=query_headers, timeout=10)
                    print(f"📊 查询响应 {i+1}: {query_response.status_code}")
                    
                    if query_response.status_code == 200:
                        query_result = query_response.json()
                        print(f"📄 查询结果: {json.dumps(query_result, ensure_ascii=False, indent=2)}")
                        
                        task_status = query_result.get("task_status", "")
                        if task_status == "SUCCEEDED":
                            output = query_result.get("output", {})
                            results = output.get("results", [])
                            if results:
                                image_url = results[0].get("url", "")
                                print(f"🎉 图像生成成功: {image_url}")
                                return True
                        elif task_status == "FAILED":
                            print(f"❌ 任务失败: {query_result}")
                            return False
                        else:
                            print(f"⏳ 任务状态: {task_status}")
                    else:
                        print(f"❌ 查询失败: {query_response.text}")
                
                print("⏰ 任务超时")
                return False
            else:
                print(f"❌ 意外的响应格式: {result}")
                return False
        else:
            print(f"❌ API调用失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_wanx_direct()