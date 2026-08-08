"""
梦境解析服务 (v2 — 增强版)
扩充符号库至 30+ 符号，支持 AI 增强分析，持久化梦境记录
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.dream import DreamRecord, DreamCreate
from app.utils.logger import logger


class DreamService:
    """梦境解析服务 — 符号检测 + 传统解梦 + AI 增强"""

    def __init__(self):
        self._symbols: dict[str, dict] = {}
        self._load_symbols()

    def _load_symbols(self):
        """加载梦境符号百科"""
        self._symbols = {
            "飞翔": {
                "category": "动作",
                "emoji": "🕊️",
                "interpretations": [
                    "象征自由和解放，渴望摆脱束缚",
                    "代表个人成长和精神提升",
                    "反映现实中的轻松愉快感",
                ],
                "related": ["坠落", "天空", "鸟"],
            },
            "坠落": {
                "category": "动作",
                "emoji": "🪂",
                "interpretations": [
                    "缺乏安全感或失去控制的感觉",
                    "焦虑或对失败的担忧",
                    "对某种情况的恐惧",
                ],
                "related": ["飞翔", "悬崖", "深渊"],
            },
            "水": {
                "category": "自然",
                "emoji": "🌊",
                "interpretations": [
                    "情感和潜意识的象征",
                    "清水表纯净，浑水表混乱",
                    "情感净化和更新的需求",
                ],
                "related": ["海", "雨", "河流", "溺"],
            },
            "火": {
                "category": "自然",
                "emoji": "🔥",
                "interpretations": [
                    "激情、愤怒或毁灭的象征",
                    "内心强烈情感或欲望",
                    "温暖火焰=热情，失控火焰=愤怒",
                ],
                "related": ["光", "烟", "炎热"],
            },
            "追逐": {
                "category": "动作",
                "emoji": "🏃",
                "interpretations": [
                    "逃避某个问题或责任",
                    "压力和焦虑感",
                    "对未来某目标的追求",
                ],
                "related": ["逃跑", "追赶", "躲藏"],
            },
            "考试": {
                "category": "场景",
                "emoji": "📝",
                "interpretations": [
                    "自我评估和表现焦虑",
                    "担心自己能力不足",
                    "对他人评价的在意",
                ],
                "related": ["学校", "教室", "失败"],
            },
            "死亡": {
                "category": "概念",
                "emoji": "💀",
                "interpretations": [
                    "很少预示真实死亡，象征转变和结束",
                    "某个阶段的结束和新开始",
                    "放下过去，迎接新生",
                ],
                "related": ["重生", "葬礼", "告别"],
            },
            "牙齿": {
                "category": "身体",
                "emoji": "🦷",
                "interpretations": [
                    "对外貌或形象的担忧",
                    "失去力量或控制感",
                    "沟通方面的焦虑",
                ],
                "related": ["口腔", "脱落", "疼痛"],
            },
            "迷路": {
                "category": "场景",
                "emoji": "🗺️",
                "interpretations": [
                    "现实生活中感到迷茫",
                    "对未来的担忧",
                    "需要重新审视目标",
                ],
                "related": ["森林", "道路", "方向"],
            },
            "蛇": {
                "category": "动物",
                "emoji": "🐍",
                "interpretations": [
                    "智慧、转变或治愈的象征",
                    "隐藏的威胁或欺骗",
                    "不同文化中的多元含义",
                ],
                "related": ["龙", "爬行", "毒"],
            },
            "门": {
                "category": "物体",
                "emoji": "🚪",
                "interpretations": [
                    "新机会或选择的象征",
                    "通向未知的入口",
                    "内心的开放或封闭状态",
                ],
                "related": ["钥匙", "锁", "房间"],
            },
            "钥匙": {
                "category": "物体",
                "emoji": "🔑",
                "interpretations": [
                    "解决问题的答案",
                    "获取新知识或能力",
                    "内心深处的解锁",
                ],
                "related": ["门", "锁", "秘密"],
            },
            "花朵": {
                "category": "自然",
                "emoji": "🌸",
                "interpretations": [
                    "美丽、爱情和温柔的象征",
                    "生命的绽放和希望",
                    "个人成长的开花结果",
                ],
                "related": ["花园", "春天", "绽放"],
            },
            "月亮": {
                "category": "自然",
                "emoji": "🌙",
                "interpretations": [
                    "潜意识、直觉和母性",
                    "情感周期的变化",
                    "神秘和未知的吸引力",
                ],
                "related": ["星星", "夜晚", "太阳"],
            },
            "太阳": {
                "category": "自然",
                "emoji": "☀️",
                "interpretations": [
                    "生命力、能量和意识",
                    "希望和光明的象征",
                    "清晰的自我认知",
                ],
                "related": ["光", "月亮", "温暖"],
            },
            "桥梁": {
                "category": "物体",
                "emoji": "🌉",
                "interpretations": [
                    "连接两个阶段的过渡",
                    "沟通和理解的桥梁",
                    "从困境到解决方案的通道",
                ],
                "related": ["河流", "道路", "过渡"],
            },
            "镜子": {
                "category": "物体",
                "emoji": "🪞",
                "interpretations": [
                    "自我反省和自我认知",
                    "真实与表象的对比",
                    "内心世界的折射",
                ],
                "related": ["影像", "反射", "自我"],
            },
            "楼梯": {
                "category": "物体",
                "emoji": "🪜",
                "interpretations": [
                    "向上=成长进步，向下=潜意识探索",
                    "人生的上升或下降阶段",
                    "目标的渐进实现",
                ],
                "related": ["电梯", "攀爬", "下降"],
            },
            "风暴": {
                "category": "自然",
                "emoji": "⛈️",
                "interpretations": [
                    "内心情感的巨大波动",
                    "即将到来的重大变化",
                    "压抑情绪的释放",
                ],
                "related": ["雨", "雷电", "风"],
            },
            "彩虹": {
                "category": "自然",
                "emoji": "🌈",
                "interpretations": [
                    "暴风雨后的希望",
                    "多元性和包容",
                    "梦想成真的预兆",
                ],
                "related": ["雨", "太阳", "光"],
            },
            "婴儿": {
                "category": "人物",
                "emoji": "👶",
                "interpretations": [
                    "新开始和纯真",
                    "内心脆弱的一面",
                    "创造力和新项目的诞生",
                ],
                "related": ["出生", "成长", "童真"],
            },
            "猫": {
                "category": "动物",
                "emoji": "🐱",
                "interpretations": [
                    "独立和直觉的象征",
                    "神秘和女性气质",
                    "内心对自由的渴望",
                ],
                "related": ["狗", "动物", "宠物"],
            },
            "狗": {
                "category": "动物",
                "emoji": "🐕",
                "interpretations": [
                    "忠诚和友谊的象征",
                    "保护和安全感",
                    "直觉和本能的指引",
                ],
                "related": ["猫", "动物", "朋友"],
            },
            "飞鸟": {
                "category": "动物",
                "emoji": "🐦",
                "interpretations": [
                    "自由和灵魂的飞翔",
                    "超脱日常事务的视角",
                    "好消息的象征",
                ],
                "related": ["飞翔", "天空", "翅膀"],
            },
            "森林": {
                "category": "自然",
                "emoji": "🌲",
                "interpretations": [
                    "潜意识的深处",
                    "未知的探索和冒险",
                    "生命力和成长的沃土",
                ],
                "related": ["树木", "迷路", "自然"],
            },
            "车": {
                "category": "物体",
                "emoji": "🚗",
                "interpretations": [
                    "人生的方向和掌控",
                    "前进的动力和速度",
                    "对人生旅程的态度",
                ],
                "related": ["道路", "驾驶", "旅行"],
            },
            "家": {
                "category": "场景",
                "emoji": "🏠",
                "interpretations": [
                    "安全感和归属感",
                    "内心世界的根基",
                    "童年记忆和根源",
                ],
                "related": ["房间", "家人", "童年"],
            },
            "食物": {
                "category": "物体",
                "emoji": "🍽️",
                "interpretations": [
                    "精神滋养和情感满足",
                    "对生活的享受和渴望",
                    "内心空虚的补偿",
                ],
                "related": ["饥饿", "宴会", "满足"],
            },
            "裸体": {
                "category": "状态",
                "emoji": "👤",
                "interpretations": [
                    "脆弱和暴露感",
                    "渴望真诚和透明",
                    "对自我形象的关注",
                ],
                "related": ["羞耻", "自由", "自我"],
            },
            "血": {
                "category": "身体",
                "emoji": "🩸",
                "interpretations": [
                    "生命力和能量的流动",
                    "情感上的深度伤害",
                    "家庭和血缘关系",
                ],
                "related": ["伤口", "生命", "家族"],
            },
            "鱼": {
                "category": "动物",
                "emoji": "🐟",
                "interpretations": [
                    "潜意识的深层内容",
                    "丰富的创造力和灵感",
                    "情感世界的探索",
                ],
                "related": ["水", "海", "潜"],
            },
        }

    def detect_symbols(self, text: str) -> list[dict]:
        """检测文本中的梦境符号"""
        detected = []
        for symbol, info in self._symbols.items():
            if symbol in text:
                detected.append({
                    "symbol": symbol,
                    "category": info["category"],
                    "emoji": info["emoji"],
                    "interpretations": info["interpretations"],
                })
        return sorted(detected, key=lambda s: len(s["symbol"]), reverse=True)

    def analyze(self, dream_text: str) -> dict:
        """传统梦境解析"""
        symbols = self.detect_symbols(dream_text)

        if not symbols:
            return {
                "detected_symbols": [],
                "analysis": "这个梦境比较独特，没有匹配到传统的解梦符号。建议结合自己的实际情况深入思考这个梦对你的意义。",
                "symbol_count": 0,
            }

        lines = []
        for item in symbols[:5]:
            lines.append(f"【{item['emoji']} {item['symbol']}】{item['interpretations'][0]}")

        analysis = "\n\n".join(lines)
        analysis += "\n\n💡 梦境是潜意识的表达，以上解读仅供参考。最重要的是结合你当前的生活状况和内心感受来理解这个梦。"

        return {
            "detected_symbols": symbols[:5],
            "analysis": analysis,
            "symbol_count": len(symbols),
        }

    async def analyze_with_ai(self, dream_text: str) -> str:
        """AI 增强梦境分析"""
        try:
            from app.services.ai_router import ai_router, TaskType, Complexity

            messages = [
                {
                    "role": "system",
                    "content": (
                        "你是一位资深的梦境解析师，擅长融合心理学（弗洛伊德、荣格）、"
                        "传统文化（周公解梦）和现代认知科学来解读梦境。"
                        "请以温暖、专业、富有洞见的口吻分析用户的梦境。"
                        "给出 200-400 字的分析，包含：1) 核心符号的象征意义 2) 可能反映的内心状态 3) 温和的建议。"
                    ),
                },
                {"role": "user", "content": f"请分析这个梦境：{dream_text}"},
            ]

            result = await ai_router.chat_completion(
                messages=messages,
                task_type=TaskType.CHAT,
                complexity=Complexity.SIMPLE,
            )
            return result["response"]
        except Exception as e:
            logger.warning(f"AI 梦境分析失败: {e}")
            return ""

    def get_symbol_encyclopedia(self, category: Optional[str] = None) -> dict:
        """获取符号百科"""
        categories = set()
        symbols_list = []

        for symbol, info in self._symbols.items():
            if category and info["category"] != category:
                continue
            categories.add(info["category"])
            symbols_list.append({
                "symbol": symbol,
                "category": info["category"],
                "emoji": info["emoji"],
                "interpretations": info["interpretations"],
                "related_symbols": info.get("related", []),
            })

        return {
            "symbols": sorted(symbols_list, key=lambda s: s["category"]),
            "categories": sorted(list(categories)),
            "total": len(symbols_list),
        }


# ── 数据库 CRUD ─────────────────────────────────────────

async def save_dream(
    session: AsyncSession,
    user_id: int,
    dream_data: DreamCreate,
    symbols: list[dict],
    analysis: str,
    ai_analysis: str = "",
) -> DreamRecord:
    """保存梦境记录"""
    dream_date = (
        datetime.fromisoformat(dream_data.dream_date)
        if dream_data.dream_date
        else datetime.now()
    )
    record = DreamRecord(
        user_id=user_id,
        dream_text=dream_data.dream_text,
        detected_symbols=json.dumps(symbols, ensure_ascii=False),
        traditional_analysis=analysis,
        ai_analysis=ai_analysis,
        analysis_type="ai_enhanced" if ai_analysis else "traditional",
        dream_date=dream_date,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_dreams(
    session: AsyncSession,
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    month: Optional[str] = None,
) -> tuple[list[DreamRecord], int]:
    """获取梦境记录列表，支持按月份筛选"""
    query = select(DreamRecord).where(DreamRecord.user_id == user_id)
    count_query = select(func.count()).select_from(DreamRecord).where(DreamRecord.user_id == user_id)

    if month:
        year, m = month.split("-")
        query = query.where(
            func.strftime("%Y-%m", DreamRecord.dream_date) == month
        )
        count_query = count_query.where(
            func.strftime("%Y-%m", DreamRecord.dream_date) == month
        )

    total = (await session.execute(count_query)).scalar() or 0

    query = query.order_by(DreamRecord.dream_date.desc()).offset(offset).limit(limit)
    result = await session.execute(query)
    items = list(result.scalars().all())

    return items, total


async def get_dream_months(session: AsyncSession, user_id: int) -> list[str]:
    """获取有梦境记录的所有月份"""
    result = await session.execute(
        select(func.strftime("%Y-%m", DreamRecord.dream_date))
        .where(DreamRecord.user_id == user_id)
        .group_by(func.strftime("%Y-%m", DreamRecord.dream_date))
        .order_by(func.strftime("%Y-%m", DreamRecord.dream_date).desc())
    )
    return [row[0] for row in result.all()]


async def get_dream_stats(session: AsyncSession, user_id: int) -> dict:
    """获取梦境统计"""
    total = (await session.execute(
        select(func.count()).select_from(DreamRecord).where(DreamRecord.user_id == user_id)
    )).scalar() or 0

    # 本月梦境数
    from datetime import datetime
    now = datetime.now()
    month_key = now.strftime("%Y-%m")
    monthly = (await session.execute(
        select(func.count()).select_from(DreamRecord).where(
            DreamRecord.user_id == user_id,
            func.strftime("%Y-%m", DreamRecord.dream_date) == month_key,
        )
    )).scalar() or 0

    # 统计最常见符号
    all_symbols = []
    result = await session.execute(
        select(DreamRecord.detected_symbols).where(DreamRecord.user_id == user_id)
    )
    for row in result.all():
        if row[0]:
            try:
                symbols = json.loads(row[0])
                all_symbols.extend(s.get("symbol", "") for s in symbols)
            except (json.JSONDecodeError, TypeError):
                pass

    from collections import Counter
    top_symbols = Counter(all_symbols).most_common(10)

    return {
        "total_dreams": total,
        "monthly_dreams": monthly,
        "top_symbols": [{"symbol": s, "count": c} for s, c in top_symbols],
    }


async def delete_dream(session: AsyncSession, dream_id: int, user_id: int) -> bool:
    """删除梦境记录"""
    result = await session.execute(
        select(DreamRecord).where(
            DreamRecord.id == dream_id,
            DreamRecord.user_id == user_id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        return False
    await session.delete(record)
    await session.commit()
    return True


    # ── 卡片生成 ─────────────────────────────────────────

    def generate_card(self, dream_text: str, symbols: list[str]) -> dict:
        """生成梦境卡片信息"""
        # 根据符号推断情绪
        mood = self._infer_mood_from_symbols(symbols)
        mood_config = {
            "happy": {"emoji": "😊", "color": "#3a7bd5", "music": "lofi-chill"},
            "sad": {"emoji": "😢", "color": "#5a4a8a", "music": "ambient-rain"},
            "neutral": {"emoji": "😐", "color": "#4a6a5a", "music": "lofi-study"},
            "anxious": {"emoji": "😰", "color": "#7a4a3a", "music": "ambient-drone"},
            "excited": {"emoji": "🤩", "color": "#d5a03a", "music": "lofi-jazz"},
            "curious": {"emoji": "🤔", "color": "#3a7b8a", "music": "lofi-explore"},
        }
        cfg = mood_config.get(mood, mood_config["neutral"])

        # 生成诗意行
        poetic_lines = {
            "happy": "在星辰的微光中，喜悦如花瓣般绽放",
            "sad": "泪滴化作雨，洗涤着夜的寂静",
            "neutral": "梦的涟漪轻抚着意识的岸边",
            "anxious": "风中的烛火摇曳，却从未熄灭",
            "excited": "心跳敲响宇宙的钟，回响不绝",
            "curious": "未知的门后，藏着千万种可能",
        }

        symbols_str = "、".join(symbols[:5]) if symbols else "未知符号"

        return {
            "title": f"{cfg['emoji']} {mood}之梦",
            "mood": mood,
            "mood_emoji": cfg["emoji"],
            "poetic_line": poetic_lines.get(mood, poetic_lines["neutral"]),
            "symbols_summary": f"梦中的{symbols_str}诉说着潜意识的秘密",
            "suggested_music": cfg["music"],
            "color_theme": cfg["color"],
        }

    def _infer_mood_from_symbols(self, symbols: list[str]) -> str:
        """从符号推断梦境情绪"""
        positive = {"飞翔", "花朵", "彩虹", "太阳", "飞鸟", "月亮"}
        negative = {"坠落", "死亡", "蛇", "风暴", "血", "迷路", "牙齿"}
        anxious = {"追逐", "考试", "裸体", "镜子"}
        excited = {"火", "车", "桥梁"}
        curious = {"门", "钥匙", "森林", "鱼", "水"}

        pos = sum(1 for s in symbols if s in positive)
        neg = sum(1 for s in symbols if s in negative)
        anx = sum(1 for s in symbols if s in anxious)
        exc = sum(1 for s in symbols if s in excited)
        cur = sum(1 for s in symbols if s in curious)

        if pos > neg and pos > anx:
            return "happy"
        if exc > 0:
            return "excited"
        if cur > 0 and anx == 0:
            return "curious"
        if anx > pos:
            return "anxious"
        if neg > pos:
            return "sad"
        return "neutral"

    def recommend_soundscape(self, symbols: list[str], mood: str = "neutral") -> dict:
        """推荐梦境音景"""
        mood = mood or self._infer_mood_from_symbols(symbols)

        soundscapes = {
            "happy": {
                "music_type": "lofi-chill",
                "description": "温暖的低保真节拍，如阳光洒落",
                "color_palette": ["#FFD93D", "#6BCB77", "#4D96FF"],
                "bpm_range": "70-90 BPM",
            },
            "sad": {
                "music_type": "ambient-rain",
                "description": "细雨般的氛围音乐，洗涤心灵",
                "color_palette": ["#5B4F8B", "#3A3D6B", "#9B8EC4"],
                "bpm_range": "50-65 BPM",
            },
            "neutral": {
                "music_type": "lofi-study",
                "description": "平静的学术节拍，伴你沉思",
                "color_palette": ["#6B8E7B", "#4A6741", "#8FA88C"],
                "bpm_range": "75-85 BPM",
            },
            "anxious": {
                "music_type": "ambient-drone",
                "description": "深沉的持续音，为不安提供锚点",
                "color_palette": ["#7B4B3A", "#5C3A2E", "#A6785E"],
                "bpm_range": "40-55 BPM",
            },
            "excited": {
                "music_type": "lofi-jazz",
                "description": "轻快的爵士节拍，随心跳起舞",
                "color_palette": ["#E8A838", "#D5693A", "#F0C75E"],
                "bpm_range": "90-110 BPM",
            },
            "curious": {
                "music_type": "lofi-explore",
                "description": "探索未知的旋律，充满可能性",
                "color_palette": ["#3A8B9A", "#5BB8C9", "#2D6E7E"],
                "bpm_range": "80-95 BPM",
            },
        }

        return soundscapes.get(mood, soundscapes["neutral"])

    def generate_world_data(self, symbols: list[dict]) -> dict:
        """生成梦境 3D 世界布局数据"""
        import math
        symbol_names = [s.get("symbol", "") for s in symbols] if symbols else ["未知"]

        # 球形行星参数
        planet_radius = 3.0
        objects = []

        for i, sym in enumerate(symbol_names[:12]):
            # 在球面上均匀分布（斐波那契球）
            phi = math.acos(1 - 2 * (i + 0.5) / max(len(symbol_names), 1))
            theta = math.pi * (1 + math.sqrt(5)) * i
            x = planet_radius * math.sin(phi) * math.cos(theta)
            y = planet_radius * math.sin(phi) * math.sin(theta)
            z = planet_radius * math.cos(phi)

            # 获取符号信息
            info = self._symbols.get(sym, {})
            emoji = info.get("emoji", "✨")
            category = info.get("category", "未知")
            interp = info.get("interpretations", ["神秘的符号"])[0]

            objects.append({
                "id": i,
                "symbol": sym,
                "emoji": emoji,
                "category": category,
                "interpretation": interp,
                "position": [round(x, 2), round(y, 2), round(z, 2)],
                "size": round(0.3 + len(sym) * 0.02, 2),
            })

        # 星球颜色方案
        mood = self._infer_mood_from_symbols(symbol_names)
        color_schemes = {
            "happy": {"land": "#4a8c5c", "water": "#3a6bd5", "sky": "#87ceeb"},
            "sad": {"land": "#4a3a5a", "water": "#2a3a6a", "sky": "#1a1a3a"},
            "neutral": {"land": "#4a6a5a", "water": "#3a5a8a", "sky": "#2a3a5a"},
            "anxious": {"land": "#6a4a3a", "water": "#5a2a1a", "sky": "#3a1a0a"},
            "excited": {"land": "#7a8a3a", "water": "#5a7a2a", "sky": "#8a9a4a"},
            "curious": {"land": "#3a7a8a", "water": "#2a5a6a", "sky": "#1a4a5a"},
        }
        colors = color_schemes.get(mood, color_schemes["neutral"])

        return {
            "planet": {"radius": planet_radius, "segments": 32},
            "colors": colors,
            "mood": mood,
            "objects": objects,
            "symbol_count": len(objects),
        }

    def generate_messenger_world(self, symbols: list[dict]) -> dict:
        """生成信使游戏世界（含 NPC 居民和任务）"""
        import math
        symbol_names = [s.get("symbol", "") for s in symbols] if symbols else []
        if not symbol_names:
            symbol_names = ["未知"]

        planet_radius = 3.0
        world_data = self.generate_world_data(symbols)

        # NPC 居民（情绪角色）
        npcs = [
            {"id": "elder", "name": "智慧长者", "emoji": "🧙", "role": "解析中心", "position": [0, planet_radius + 1.0, 0]},
            {"id": "child", "name": "好奇小孩", "emoji": "👧", "role": "信使助手", "position": [planet_radius - 0.5, 0.5, 0]},
            {"id": "guardian", "name": "梦境守护者", "emoji": "🛡️", "role": "引导者", "position": [0, -planet_radius + 0.5, 0]},
        ]

        # 任务列表
        quests = []
        for i, sym in enumerate(symbol_names[:8]):
            info = self._symbols.get(sym, {})
            quests.append({
                "id": f"quest_{i}",
                "symbol": sym,
                "emoji": info.get("emoji", "✨"),
                "letter": f"亲爱的{sym}：{info.get('interpretations', ['你承载着深层含义'])[0][:50]}...",
                "target_npc": sym,
                "score": 10 + len(sym) * 2,
                "completed": False,
            })

        world_data["npcs"] = npcs
        world_data["quests"] = quests
        world_data["game_mode"] = "messenger"
        world_data["total_score"] = sum(q["score"] for q in quests)

        return world_data

    def get_messenger_rank(self, score: int) -> str:
        """根据分数返回信使等级"""
        if score >= 100:
            return "🌟 梦境大师"
        if score >= 60:
            return "📬 资深信使"
        if score >= 30:
            return "✉️ 见习信使"
        return "🌱 初入梦境"


# 全局单例
dream_service = DreamService()
