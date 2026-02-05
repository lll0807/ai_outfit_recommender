import os
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv
import asyncio
from agent.weather_agent import WeatherAgent

load_dotenv()
RECOMMEND_AGENT_PROMPT = """
你是一个穿衣推荐智能体，擅长根据天气信息和用户需求，给出实用、合理的穿衣建议。

你将接收两类输入信息：
1. 天气数据（JSON 格式），可能包含：
   - 日期（date）
   - 白天/夜间天气状况（dayweather, nightweather）
   - 白天/夜间温度（daytemp, nighttemp）
   - 风向、风力（daywind, daypower）
2. 用户的原始查询（自然语言）

你的任务是：
- 正确理解天气信息，不要臆造不存在的数据
- 重点关注以下穿衣相关因素：
  - 气温高低（尤其是最低/最高温）
  - 昼夜温差
  - 天气状况（晴、雨、雪、大风等）
- 结合用户查询语境（如是否出行、是否早晚活动）
- 给出【清晰、具体、可执行】的穿衣建议

输出要求：
- 使用自然、友好的中文
- 直接给出建议，不要解释你的推理过程
- 不要输出 JSON，不要提及“根据数据”“系统提示”等内部信息
- 如果天气较冷，明确指出外套类型（如：羽绒服、棉服、厚外套）
- 如果温差较大，提醒“早晚注意保暖”
- 如有必要，可附带简单的生活建议（如防风、防晒）

请根据实际输入灵活生成回答。
"""

class RecommendAgent:
    def __init__(self):
        print("🔄 开始初始推荐agent...")
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        self.weather_agent = WeatherAgent()

    def _build_query(self, weather_data, user_input):
        query = f"""
        你将接收到两部分信息：
        【天气数据】：
        {weather_data}

        【用户需求】：
        {user_input}

        请基于以上信息，为用户提供【具体、实用的穿衣建议】。

        要求：
        1. 重点考虑气温高低、昼夜温差、天气状况（如晴、雨、大风等）
        2. 明确给出外套类型、内搭建议（如羽绒服/厚外套/毛衣等）
        3. 如昼夜温差较大，请提醒早晚注意保暖
        4. 不要输出 JSON、不要解释推理过程
        """

        return query

    def call_llm_api_stream(self, messages: List[Dict], max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                stream = self.client.chat.completions.create(
                    model=os.getenv("LLM_MODEL_ID"),
                    messages=messages,
                    temperature=0.3,
                    max_tokens=2048,
                    stream=True
                )

                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content

                return
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e

    def run(self, user_input):
        weather_data = self.weather_agent.run(user_input)
        if not weather_data["success"]:
            return "我只能查询未来4天的天气"
        query = self._build_query(weather_data, user_input)

        messages = [
            {"role": "system", "content": RECOMMEND_AGENT_PROMPT},
            {"role": "user", "content": query}
        ]

        full_response = ""
        for chunk in self.call_llm_api_stream(messages):
            print(chunk, end="", flush=True)   # 👈 实时输出
            full_response += chunk

        print()  # 换行
        return full_response

    async def run_stream(self, user_input: str):
        """异步流式返回推荐内容"""
        weather_data = await asyncio.to_thread(self.weather_agent.run, user_input)
        if not weather_data["success"]:
            yield "我只能查询未来4天的天气"
            return

        query = self._build_query(weather_data, user_input)
        messages = [
            {"role": "system", "content": RECOMMEND_AGENT_PROMPT},
            {"role": "user", "content": query}
        ]

        for chunk in self.call_llm_api_stream(messages):
            yield chunk