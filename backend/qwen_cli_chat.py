#!/usr/bin/env python3
"""
Command line chat interface for testing Qwen integration.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    print("🎬 Spark AI 视频创意助手 - 命令行版本")
    print("=" * 45)
    print("💡 输入 'quit' 或 'exit' 退出")
    print("💡 输入 'structure' 结构化当前对话")
    print("💡 输入 'clear' 清空对话历史")
    print()
    
    try:
        from spark.chatbot.core import ChatbotCore
        from spark.chatbot.idea_structurer import IdeaStructurer
        
        # Initialize components
        chatbot_core = ChatbotCore()
        idea_structurer = IdeaStructurer()
        
        print("✅ Qwen 聊天机器人已初始化")
        print("🤖 你好！我是你的视频创意助手。请告诉我你想创建什么样的视频？")
        print()
        
        conversation_started = False
        
        while True:
            try:
                user_input = input("👤 你: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 再见！")
                    break
                
                if user_input.lower() in ['clear', '清空']:
                    chatbot_core.reset_conversation()
                    conversation_started = False
                    print("🧹 对话历史已清空")
                    continue
                
                if user_input.lower() in ['structure', '结构化']:
                    print("📝 正在结构化对话...")
                    try:
                        conversation_history = chatbot_core.get_conversation_history()
                        if conversation_history:
                            user_idea = idea_structurer.structure_conversation(conversation_history)
                            if user_idea:
                                print("✅ 结构化成功！")
                                print("📋 结构化结果:")
                                import json
                                print(json.dumps(user_idea.model_dump(), ensure_ascii=False, indent=2))
                            else:
                                print("❌ 结构化失败")
                        else:
                            print("⚠️  没有对话历史可以结构化")
                    except Exception as e:
                        print(f"❌ 结构化错误: {e}")
                    continue
                
                if not user_input:
                    continue
                
                print("🤖 AI正在思考...")
                
                # Get response from chatbot
                if not conversation_started:
                    response_data = chatbot_core.engage_user(user_input)
                    conversation_started = True
                else:
                    response_data = chatbot_core.continue_conversation(user_input)
                
                # Display response
                if response_data.get("status") == "error":
                    print(f"❌ 错误: {response_data.get('error', '未知错误')}")
                else:
                    print(f"🤖 AI: {response_data.get('response', '抱歉，我无法回应。')}")
                    
                    # Show completeness info
                    is_complete = response_data.get("is_complete", False)
                    missing_elements = response_data.get("missing_elements", [])
                    
                    if is_complete:
                        print("✅ 创意信息收集完整！可以输入 'structure' 进行结构化。")
                    elif missing_elements:
                        print(f"📝 还需要了解: {', '.join(missing_elements)}")
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
                continue
    
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()