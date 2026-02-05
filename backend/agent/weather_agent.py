import os
from typing import Dict, Any, List
import time
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
import asyncio
import re
import json
from datetime import datetime, date

load_dotenv()
WEATHER_AGENT_PROMPT = """你是天气查询专家。你的任务是查询指定城市的天气信息。

**重要提示:**
1.你必须使用工具来查询指定日期的天气!不要自己编造天气信息!
2.你需要从用户的输入中分析需要查询天气的城市和日期，如果用户没有输入日期，默认为date=0000

**工具调用格式:**
使用maps_weather工具时,必须严格按照以下格式:
`[city=城市名, date=日期]`

**示例:**
用户: "查询北京天气"
你的回复: [city=北京, date=0000]

用户: "我想查询2月6号的北京天气"
你的回复: [city=北京, date=2026-02-06]

用户: "2月4号上海的天气怎么样"
你的回复: [city=上海, date=2026-02-04]

**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
"""

class WeatherAgent:

    def __init__(self):
        print("🔄 开始初始天气agent...")
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )

        # 创建共享的MCP工具(只创建一次)
        print("  - 创建MCP工具...")
        self.server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@amap/amap-maps-mcp-server"],
            env={"AMAP_MAPS_API_KEY": os.getenv("AMAP_API_KEY")}
        )

    # 解析llm输出
    def parse_params(self, text: str) -> Dict[str, str]:
        """
        从形如 [city=上海, date=2026-02-04] 的字符串中解析参数
        """
        # 1️⃣ 先取出 [] 中的内容
        bracket_match = re.search(r"\[([^\]]+)\]", text)
        if not bracket_match:
            return {}

        inner = bracket_match.group(1)  # "city=上海, date=2026-02-04"

        # 2️⃣ 按逗号分割 key=value
        params = {}
        for part in inner.split(","):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            params[key.strip()] = value.strip()

        return params

    async def _query_weather(self, city: str):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "maps_weather",
                    {"city": city}
                )
                return result

    def call_llm_api(self, messages: List[Dict], max_retries: int = 3) -> str:
        """调用LLM"""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=os.getenv("LLM_MODEL_ID"),
                    messages=messages,
                    temperature=0.3,
                    max_tokens=2048,
                    stream=False
                )

                return response.choices[0].message.content

            except Exception as e:
                print(f"API调用错误 (尝试 {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避

    def days_from_today(self, target_date: str) -> int:
        """
        计算目标日期与当天日期的天数差
        :param target_date: 'YYYY-MM-DD'
        :return: 相差天数（未来为正，过去为负）
        """
        target = datetime.strptime(target_date, "%Y-%m-%d").date()
        today = date.today()
        return (target - today).days

    def parse_weather_result(self, result, cha):
        """
        从 MCP maps_weather 返回结果中解析 JSON
        """
        if not result or not result.content:
            raise ValueError("Empty weather result")

        text = result.content[0].text
        weather_data = json.loads(text)
        today = weather_data["forecasts"][cha]

        return {
            "city": weather_data["city"],
            "date": today["date"],
            "day_temp": float(today["daytemp_float"]),
            "night_temp": float(today["nighttemp_float"]),
            "weather": today["dayweather"],
            "wind": today["daywind"],
            "wind_power": today["daypower"],
            "success": True,
        }

    def run(self, query=""):
        print("🌤️ 查询天气...")
        messages = [
            {"role": "system", "content": WEATHER_AGENT_PROMPT},
            {"role": "user", "content": query}
        ]
        response = self.call_llm_api(messages)
        params = self.parse_params(response)
        city_name, date = params["city"], params["date"]

        if date == "0000":
            cha = 0
        else:
            cha = self.days_from_today(date)
        if cha < 0 or cha > 4:
            print(f"{cha}  查询失败")
            return {"success": False}

        result = asyncio.run(self._query_weather(city_name))
        print("🌤️ 查询天气结束...")
        weather_result = self.parse_weather_result(result, cha)
        return weather_result

