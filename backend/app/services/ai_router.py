"""
AI 多模型路由器 - 核心 MCP 调度引擎

职责:
1. 管理多个 AI 提供方 (DeepSeek, OpenAI, Qwen, 豆包, Kimi, Claude...)
2. 智能路由: 根据任务类型/成本/延迟选择最优模型
3. 故障转移: 模型失败时自动切换到备用模型
4. 负载均衡: 多 API Key 轮询
5. 流式输出: SSE 支持
6. 上下文管理: 对话历史自动维护
7. 模型协作: 复杂任务分解与多模型协同
8. 结果聚合: 整合多模型输出为最终答案

API 调用规则:
- 所有兼容 OpenAI 格式的 API 统一使用 /chat/completions 端点
- Authorization: Bearer {api_key}
- 请求体: { model, messages, temperature, max_tokens, stream }
- 故障转移: 当前模型失败 → 同提供方其他模型 → 其他提供方最低成本模型
"""

from __future__ import annotations

import json
import time
import random
import asyncio
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import AsyncGenerator, Optional, List, Dict, Any

import httpx

from app.config.settings import settings
from app.config.constants import Constants
from app.utils.logger import logger


class TaskType(str, Enum):
    """任务类型 - 用于智能路由决策"""
    CHAT = "chat"            # 普通对话
    REASONING = "reasoning"  # 深度推理 (需要思考模式)
    CODE = "code"            # 代码生成
    VISION = "vision"        # 图像理解
    EMOTION = "emotion"      # 情感分析
    TRANSLATE = "translate"  # 翻译
    SUMMARIZE = "summarize"  # 摘要
    COMPLEX = "complex"      # 复杂任务（需要多模型协作）


class Complexity(str, Enum):
    """任务复杂度"""
    SIMPLE = "simple"    # 简单任务 (Flash 级别够用)
    MEDIUM = "medium"    # 中等任务 (Pro 级别)
    HARD = "hard"        # 复杂任务 (顶级模型)
    COMPLEX = "complex"  # 超复杂任务（需要协作）


class SubTaskType(str, Enum):
    """子任务类型 - 用于任务分解"""
    RETRIEVAL = "retrieval"      # 信息检索
    REASONING = "reasoning"      # 逻辑推理
    ANALYSIS = "analysis"        # 数据分析
    SYNTHESIS = "synthesis"      # 综合总结
    CREATION = "creation"        # 创意生成
    VERIFICATION = "verification" # 验证校验
    CODING = "coding"            # 代码编写


@dataclass
class ModelInfo:
    """模型信息"""
    provider: str
    model_name: str
    api_key: str
    endpoint: str
    cost_per_1k: float  # 每千token成本 (美元)
    capabilities: set[str] = field(default_factory=set)
    priority: int = 0    # 优先级 (数字越小越优先)
    is_available: bool = True
    latency_ms: float = 0.0


@dataclass
class RoutingDecision:
    """路由决策结果"""
    provider: str
    model_name: str
    endpoint: str
    api_key: str
    reasoning: str  # 选择理由


@dataclass
class SubTaskResult:
    """子任务执行结果"""
    subtask_type: SubTaskType
    model_provider: str
    model_name: str
    content: str
    confidence: float = 0.0  # 置信度 (0-1)
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationPlan:
    """协作计划 - 描述如何分解和执行复杂任务"""
    original_task: str
    subtasks: List[Dict[str, Any]]  # [{type, description, assigned_model}]
    aggregation_strategy: str  # "sequential", "parallel", "voting"
    estimated_cost: float = 0.0
    reasoning: str = ""


@dataclass
class AggregatedResult:
    """聚合结果"""
    final_response: str
    subtask_results: List[SubTaskResult]
    collaboration_summary: str
    total_cost: float
    total_time_ms: float
    models_used: List[str]


class AIRouter:
    """
    AI 路由器 - 单例
    
    管理所有 AI 提供方，提供智能路由能力。
    使用连接池复用的 httpx.AsyncClient 提升性能。
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    def __init__(self):
        if self._initialized:
            return

        self.models: list[ModelInfo] = []
        self._http_client: Optional[httpx.AsyncClient] = None
        self._load_pricing()
        self._load_providers()
        self._initialized = True
        logger.info(
            f"AI Router 初始化完成: {len(self.models)} 个模型可用"
        )

    def _load_pricing(self):
        """从 JSON 配置文件加载模型价格"""
        import json
        pricing_path = Path(__file__).parent.parent.parent / "config" / "model_pricing.json"
        try:
            with open(pricing_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._pricing = {k: v for k, v in data.items() if isinstance(v, dict)}
            self._default_cost = data.get("default_cost", 0.1)
            logger.debug(f"模型价格配置已加载 ({len(self._pricing)} 提供方)")
        except Exception as e:
            logger.warning(f"加载模型价格配置失败: {e}，使用默认价格")
            self._pricing = {}
            self._default_cost = 0.1

    async def _get_http_client(self) -> httpx.AsyncClient:
        """获取共享的 httpx 客户端（连接池复用）"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(120.0, connect=10.0),
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=50,
                    keepalive_expiry=30.0,
                ),
            )
        return self._http_client

    async def close_http_client(self):
        """关闭 HTTP 客户端连接池"""
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None
            logger.info("HTTP 客户端连接池已关闭")

    def _load_providers(self):
        """从配置加载所有 AI 提供方"""
        providers = settings.get_all_api_keys()

        for provider_name, config in providers.items():
            for model_name in config["models"]:
                # 定义各模型能力
                capabilities = self._get_model_capabilities(provider_name, model_name)
                cost = self._get_model_cost(provider_name, model_name)
                priority = self._get_model_priority(provider_name, model_name)

                model = ModelInfo(
                    provider=provider_name,
                    model_name=model_name,
                    api_key=config["api_key"],
                    endpoint=config.get("endpoint", ""),
                    cost_per_1k=cost,
                    capabilities=capabilities,
                    priority=priority,
                )
                self.models.append(model)

        # 按优先级排序
        self.models.sort(key=lambda m: (m.priority, m.cost_per_1k))

    def _get_model_capabilities(
        self, provider: str, model_name: str
    ) -> set[str]:
        """获取模型能力集"""
        caps = {"chat"}

        # DeepSeek
        if provider == "deepseek":
            caps.add("code")
            if "reasoner" in model_name:
                caps.add("reasoning")
                caps.add("thinking")

        # OpenAI
        if provider == "openai":
            caps.add("code")
            caps.add("vision")
            if "gpt-4" in model_name and "mini" not in model_name:
                caps.add("reasoning")
            if "o1" in model_name or "o3" in model_name:
                caps.add("reasoning")
                caps.add("thinking")

        # Qwen (通义千问)
        if provider == "qwen":
            caps.add("code")
            caps.add("vision")
            if "max" in model_name:
                caps.add("reasoning")

        # Doubao (豆包/火山引擎)
        if provider == "doubao":
            caps.add("code")
            # doubao-pro 系列支持长上下文
            if "128k" in model_name:
                caps.add("long_context")

        # Kimi (月之暗面)
        if provider == "kimi":
            caps.add("code")
            caps.add("long_context")  # Kimi 默认支持长上下文
            if "32k" in model_name:
                caps.add("reasoning")

        return caps

    def _get_model_cost(self, provider: str, model_name: str) -> float:
        """获取模型成本 (每千token USD)，从 model_pricing.json 加载"""
        return self._pricing.get(provider, {}).get(model_name, self._default_cost)

    def _get_model_priority(self, provider: str, model_name: str) -> int:
        """获取模型优先级 (数字越小优先级越高)"""
        # 优先级策略: 低成本 → 国内优先 → 高质量
        # 第1梯队: 低成本模型
        if any(kw in model_name for kw in ("turbo", "mini", "chat")):
            return 1
        # 第2梯队: 中等模型
        if any(kw in model_name for kw in ("plus", "8k", "32k")):
            return 2
        # 第3梯队: 高端模型
        if any(kw in model_name for kw in ("max", "pro", "reasoner")):
            return 3
        # 第4梯队: 超高端模型
        if any(kw in model_name for kw in ("turbo", "4o")):
            return 4
        return 5

    def resolve_provider(self, name: str) -> Optional[str]:
        """
        解析提供方名称：支持传入提供方名或模型名
        
        Args:
            name: 提供方名称 (如 "deepseek") 或模型名称 (如 "deepseek-chat")
            
        Returns:
            提供方名称，未找到返回 None
        """
        # 直接匹配提供方
        providers = self.get_providers()
        if name in providers:
            return name
        
        # 按模型名称查找
        for provider, config in providers.items():
            if name in config.get("models", []):
                return provider
        
        # 按模型名前缀匹配
        for model in self.models:
            if model.model_name == name:
                return model.provider
            if model.provider == name:
                return name
        
        return None

    def route(self, task_type: TaskType = TaskType.CHAT,
              complexity: Complexity = Complexity.SIMPLE,
              preferred_provider: Optional[str] = None,
              max_cost: Optional[float] = None) -> RoutingDecision:
        """
        智能路由 - 选择最优模型

        Args:
            task_type: 任务类型
            complexity: 任务复杂度
            preferred_provider: 首选提供方（支持提供方名或模型名）
            max_cost: 最大成本限制

        Returns:
            RoutingDecision: 路由决策
        """
        candidates = list(self.models)

        # 1. 按首选提供方/模型过滤
        if preferred_provider:
            resolved = self.resolve_provider(preferred_provider)
            if resolved:
                candidates = [m for m in candidates if m.provider == resolved]
            else:
                logger.warning(f"未找到提供方/模型: {preferred_provider}，忽略该偏好")

        # 2. 按能力过滤
        task_caps = self._task_required_capabilities(task_type)
        candidates = [
            m for m in candidates
            if task_caps.issubset(m.capabilities)
        ]

        # 3. 按复杂度选择:
        #    - SIMPLE: 最低优先级的可用模型
        #    - MEDIUM: 中等优先级
        #    - HARD: 最高能力模型
        if complexity == Complexity.HARD:
            # 选能力最强的 (按优先级降序，但能力要最全)
            candidates.sort(key=lambda m: (-len(m.capabilities), m.priority))
        else:
            # 选成本最低的 - 但对于相同优先级的模型，随机选择以增加多样性
            candidates.sort(key=lambda m: (m.priority, m.cost_per_1k))
            
            # 增加模型多样性：如果候选模型数量 > 1，随机选择一个同优先级的模型
            if len(candidates) > 1:
                # 找出所有优先级相同的候选模型
                best_priority = candidates[0].priority
                same_priority_models = [m for m in candidates if m.priority == best_priority]
                
                # 如果有多个同优先级模型，随机选择一个
                if len(same_priority_models) > 1:
                    chosen = random.choice(same_priority_models)
                    reasoning = (
                        f"智能路由(随机): task={task_type.value}, complexity={complexity.value} → "
                        f"{chosen.provider}/{chosen.model_name} "
                        f"(cost=${chosen.cost_per_1k}/1k tokens)"
                    )
                    
                    return RoutingDecision(
                        provider=chosen.provider,
                        model_name=chosen.model_name,
                        endpoint=chosen.endpoint,
                        api_key=chosen.api_key,
                        reasoning=reasoning,
                    )

        # 4. 按成本过滤
        if max_cost is not None:
            candidates = [m for m in candidates if m.cost_per_1k <= max_cost]

        if not candidates:
            # 降级: 任意可用模型
            candidates = [
                m for m in self.models if m.is_available
            ]
            if not candidates:
                raise RuntimeError("没有可用的 AI 模型")

            chosen = candidates[0]
            reasoning = f"⚠️ 降级选择（无符合条件模型）: {chosen.provider}/{chosen.model_name}"
        else:
            chosen = candidates[0]
            reasoning = (
                f"智能路由: task={task_type.value}, complexity={complexity.value} → "
                f"{chosen.provider}/{chosen.model_name} "
                f"(cost=${chosen.cost_per_1k}/1k tokens)"
            )

        return RoutingDecision(
            provider=chosen.provider,
            model_name=chosen.model_name,
            endpoint=chosen.endpoint,
            api_key=chosen.api_key,
            reasoning=reasoning,
        )

    def _task_required_capabilities(self, task_type: TaskType) -> set[str]:
        """任务所需的能力集"""
        mapping = {
            TaskType.CHAT: {"chat"},
            TaskType.REASONING: {"chat", "reasoning", "thinking"},
            TaskType.CODE: {"chat", "code"},
            TaskType.VISION: {"chat", "vision"},
            TaskType.EMOTION: {"chat"},
            TaskType.TRANSLATE: {"chat"},
            TaskType.SUMMARIZE: {"chat"},
        }
        return mapping.get(task_type, {"chat"})

    async def chat_completion(
        self,
        messages: list[dict],
        task_type: TaskType = TaskType.CHAT,
        complexity: Complexity = Complexity.SIMPLE,
        preferred_provider: Optional[str] = None,
        stream: bool = False,
    ) -> dict | AsyncGenerator[str, None]:
        """
        聊天补全 (自动路由)

        Args:
            messages: OpenAI 格式的消息列表
            task_type: 任务类型
            complexity: 复杂度
            preferred_provider: 首选提供方
            stream: 是否流式输出

        Returns:
            dict: 包含 response, model_name, usage 等
            或 AsyncGenerator (stream=True)
        """
        decision = self.route(task_type, complexity, preferred_provider)

        if stream:
            return self._stream_chat(decision, messages)
        else:
            return await self._sync_chat(decision, messages)

    def _mark_model_unavailable(self, provider: str, model_name: str):
        """标记指定模型为不可用"""
        for model in self.models:
            if model.provider == provider and model.model_name == model_name:
                model.is_available = False
                logger.warning(f"模型已标记为不可用: {provider}/{model_name}")
                break

    def _reset_model_availability(self):
        """重置所有模型为可用状态（定时恢复）"""
        for model in self.models:
            model.is_available = True

    async def _sync_chat(
        self, decision: RoutingDecision, messages: list[dict]
    ) -> dict:
        """同步聊天补全（含故障转移和多模型容错）"""
        # 记录已尝试过的模型，避免无限重试
        attempted_models: set[str] = set()

        for attempt in range(Constants.API_MAX_RETRIES * 2):  # 允许更多尝试（跨模型）
            model_key = f"{decision.provider}/{decision.model_name}"
            
            # 跳过已尝试过的模型
            if model_key in attempted_models:
                # 尝试其他提供方
                decision = self._failover(decision.provider)
                continue
            
            attempted_models.add(model_key)

            payload = {
                "model": decision.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 4096,
                "stream": False,
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {decision.api_key}",
            }

            try:
                client = await self._get_http_client()
                start = time.time()
                resp = await client.post(
                    decision.endpoint, json=payload, headers=headers
                )
                resp.raise_for_status()
                data = resp.json()
                latency = (time.time() - start) * 1000

                # 更新延迟信息
                for model in self.models:
                    if model.model_name == decision.model_name:
                        model.latency_ms = latency

                choice = data["choices"][0]
                usage = data.get("usage", {})

                return {
                    "response": choice["message"]["content"],
                    "model_name": decision.model_name,
                    "provider": decision.provider,
                    "usage": {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                    "latency_ms": latency,
                    "reasoning": decision.reasoning,
                }

            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                logger.warning(
                    f"模型 {decision.model_name} HTTP {status} 错误 "
                    f"(尝试 {attempt + 1}): {e}"
                )
                
                # 401/403 = 认证失败，标记该提供方所有模型不可用
                if status in (401, 403):
                    self._mark_model_unavailable(decision.provider, decision.model_name)
                    # 也标记该提供方的其他模型
                    for model in self.models:
                        if model.provider == decision.provider:
                            model.is_available = False
                
                # 429 = 限流，尝试其他模型
                # 5xx = 服务端错误，尝试其他模型
                decision = self._failover(decision.provider)

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                logger.warning(
                    f"模型 {decision.model_name} 连接失败 "
                    f"(尝试 {attempt + 1}): {e}"
                )
                # 连接失败，标记该模型不可用
                self._mark_model_unavailable(decision.provider, decision.model_name)
                decision = self._failover(decision.provider)

            except Exception as e:
                logger.warning(
                    f"模型 {decision.model_name} 未知错误 "
                    f"(尝试 {attempt + 1}): {e}"
                )
                decision = self._failover(decision.provider)

        # 所有尝试都失败
        raise RuntimeError(
            f"所有可用模型均请求失败，已尝试: {', '.join(attempted_models)}"
        )

    async def _stream_chat(
        self, decision: RoutingDecision, messages: list[dict]
    ) -> AsyncGenerator[str, None]:
        """流式聊天补全 (SSE) - 含故障转移"""
        attempted_models: set[str] = set()

        for attempt in range(Constants.API_MAX_RETRIES * 2):
            model_key = f"{decision.provider}/{decision.model_name}"
            if model_key in attempted_models:
                decision = self._failover(decision.provider)
                continue
            attempted_models.add(model_key)

            payload = {
                "model": decision.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 4096,
                "stream": True,
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {decision.api_key}",
            }

            try:
                client = await self._get_http_client()
                async with client.stream(
                    "POST", decision.endpoint, json=payload, headers=headers
                ) as resp:
                        resp.raise_for_status()
                        async for line in resp.aiter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:]
                                if data_str.strip() == "[DONE]":
                                    break
                                try:
                                    chunk = json.loads(data_str)
                                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                                except json.JSONDecodeError:
                                    continue
                        # 流成功完成，退出
                        return

            except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError) as e:
                logger.warning(
                    f"流式模型 {decision.model_name} 请求失败 "
                    f"(尝试 {attempt + 1}): {e}"
                )
                self._mark_model_unavailable(decision.provider, decision.model_name)
                decision = self._failover(decision.provider)

        raise RuntimeError(
            f"所有流式模型均请求失败，已尝试: {', '.join(attempted_models)}"
        )

    def _failover(self, failed_provider: str) -> RoutingDecision:
        """
        故障转移 - 当当前模型/提供方失败时选择下一个

        Args:
            failed_provider: 失败的提供方名称

        Returns:
            RoutingDecision: 新的路由决策
        """
        # 排除失败的提供方，只选可用模型
        candidates = [
            m for m in self.models
            if m.provider != failed_provider and m.is_available
        ]

        if not candidates:
            # 如果排除后没有可用模型，尝试所有仍在可用列表中的模型
            candidates = [
                m for m in self.models if m.is_available
            ]

        if not candidates:
            raise RuntimeError("所有 AI 模型都不可用，无法故障转移")

        # 选择成本最低 + 优先级最高的
        candidates.sort(key=lambda m: (m.priority, m.cost_per_1k))
        chosen = candidates[0]

        reasoning = (
            f"故障转移: {failed_provider} 不可用 → "
            f"{chosen.provider}/{chosen.model_name} "
            f"(cost=${chosen.cost_per_1k}/1k tokens)"
        )
        logger.warning(reasoning)

        return RoutingDecision(
            provider=chosen.provider,
            model_name=chosen.model_name,
            endpoint=chosen.endpoint,
            api_key=chosen.api_key,
            reasoning=reasoning,
        )

    def get_available_models(self) -> list[dict]:
        """获取所有可用模型信息"""
        return [
            {
                "provider": m.provider,
                "model": m.model_name,
                "cost_per_1k": m.cost_per_1k,
                "capabilities": list(m.capabilities),
                "priority": m.priority,
                "latency_ms": m.latency_ms,
            }
            for m in self.models
        ]

    def get_providers(self) -> dict:
        """获取所有已配置的提供方"""
        return settings.get_all_api_keys()

    # ==================== 模型协作与聚合功能 ====================

    async def collaborative_chat(
        self,
        messages: list[dict],
        task_type: TaskType = TaskType.COMPLEX,
        enable_collaboration: bool = True,
    ) -> Dict[str, Any]:
        """
        协作式聊天 - 对复杂任务进行多模型协同处理

        Args:
            messages: OpenAI 格式的消息列表
            task_type: 任务类型（默认 COMPLEX）
            enable_collaboration: 是否启用协作模式

        Returns:
            dict: 包含最终响应、子任务结果、协作摘要等
        """
        if not enable_collaboration or task_type != TaskType.COMPLEX:
            # 非复杂任务或非协作模式，使用标准路由
            decision = self.route(task_type, Complexity.HARD)
            result = await self._sync_chat(decision, messages)
            return {
                **result,
                "collaboration_used": False,
            }

        logger.info("🤝 启动多模型协作模式")
        start_time = time.time()

        # 1. 任务分解
        plan = await self._decompose_task(messages)
        logger.info(f"📋 协作计划: {len(plan.subtasks)} 个子任务")

        # 2. 并行执行子任务
        subtask_results = await self._execute_subtasks(plan, messages)
        logger.info(f"✅ 完成 {len(subtask_results)} 个子任务")

        # 3. 结果聚合
        aggregated = await self._aggregate_results(plan, subtask_results, messages)

        total_time = (time.time() - start_time) * 1000

        return {
            "response": aggregated.final_response,
            "model_name": "collaborative-multi-model",
            "provider": "multi-provider",
            "usage": {
                "prompt_tokens": sum(r.metadata.get("prompt_tokens", 0) for r in subtask_results),
                "completion_tokens": sum(r.metadata.get("completion_tokens", 0) for r in subtask_results),
                "total_tokens": sum(r.metadata.get("total_tokens", 0) for r in subtask_results),
            },
            "latency_ms": total_time,
            "reasoning": aggregated.collaboration_summary,
            "collaboration_used": True,
            "subtask_results": [
                {
                    "type": r.subtask_type.value,
                    "model": f"{r.model_provider}/{r.model_name}",
                    "content_preview": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                    "confidence": r.confidence,
                    "execution_time_ms": r.execution_time_ms,
                }
                for r in subtask_results
            ],
            "models_used": aggregated.models_used,
            "total_cost": aggregated.total_cost,
        }

    async def _decompose_task(self, messages: list[dict]) -> CollaborationPlan:
        """
        任务分解器 - 将复杂任务分解为多个子任务

        策略:
        1. 分析任务的复杂性维度
        2. 识别需要的专业能力（检索、推理、代码、总结等）
        3. 制定执行顺序和依赖关系
        4. 为每个子任务分配最适合的模型
        """
        user_message = messages[-1]["content"] if messages else ""

        # 使用轻量级模型进行任务分析
        analysis_decision = self.route(TaskType.REASONING, Complexity.MEDIUM)

        decomposition_prompt = f"""
你是一个任务分解专家。请分析以下用户请求，并将其分解为多个可独立执行的子任务。

用户请求:
{user_message}

请按照以下 JSON 格式返回分解结果：
{{
  "subtasks": [
    {{
      "type": "retrieval|reasoning|analysis|synthesis|creation|verification|coding",
      "description": "子任务的详细描述",
      "required_capabilities": ["chat", "code", "reasoning", ...],
      "priority": 1-10 (数字越小优先级越高),
      "depends_on": [] (依赖的子任务索引，空数组表示无依赖)
    }}
  ],
  "aggregation_strategy": "sequential|parallel|voting",
  "estimated_complexity": "medium|hard|complex"
}}

分解原则:
1. retrieval: 需要查找事实、数据、最新信息
2. reasoning: 需要逻辑推理、因果分析、问题求解
3. analysis: 需要数据分析、模式识别、趋势判断
4. synthesis: 需要综合多个信息源、总结归纳
5. creation: 需要创意生成、内容创作、方案设计
6. verification: 需要验证正确性、检查一致性
7. coding: 需要编写、调试、优化代码

注意:
- 如果任务简单，只返回 1-2 个子任务
- 如果任务复杂，可以返回 3-5 个子任务
- 确保子任务之间有清晰的边界
- 考虑子任务之间的依赖关系
"""

        try:
            client = await self._get_http_client()
            resp = await client.post(
                analysis_decision.endpoint,
                json={
                    "model": analysis_decision.model_name,
                    "messages": [
                        {"role": "system", "content": "你是任务分解专家"},
                        {"role": "user", "content": decomposition_prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2048,
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {analysis_decision.api_key}",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            plan_data = json.loads(data["choices"][0]["message"]["content"])

            # 构建协作计划
            subtasks = []
            for idx, st in enumerate(plan_data.get("subtasks", [])):
                # 为每个子任务选择最合适的模型
                required_caps = set(st.get("required_capabilities", ["chat"]))
                assigned_model = self._select_best_model_for_capability(required_caps)

                subtasks.append({
                    "index": idx,
                    "type": st["type"],
                    "description": st["description"],
                    "assigned_model": assigned_model,
                    "priority": st.get("priority", 5),
                    "depends_on": st.get("depends_on", []),
                })

            return CollaborationPlan(
                original_task=user_message,
                subtasks=subtasks,
                aggregation_strategy=plan_data.get("aggregation_strategy", "parallel"),
                estimated_cost=sum(
                    self._get_model_cost(m.provider, m.model_name) 
                    for m in [st["assigned_model"] for st in subtasks]
                ),
                reasoning=f"任务分解为 {len(subtasks)} 个子任务，采用 {plan_data.get('aggregation_strategy', 'parallel')} 策略",
            )

        except Exception as e:
            logger.error(f"任务分解失败: {e}，使用默认分解策略")
            # 降级：使用默认分解策略
            return self._default_decomposition(user_message)

    def _default_decomposition(self, user_message: str) -> CollaborationPlan:
        """默认任务分解策略（当 AI 分解失败时使用）"""
        # 基于关键词的简单启发式分解
        subtasks = []

        if any(kw in user_message.lower() for kw in ["代码", "code", "编程", "program"]):
            subtasks.append({
                "index": 0,
                "type": "coding",
                "description": "编写或分析代码",
                "assigned_model": self._select_best_model_for_capability({"chat", "code"}),
                "priority": 1,
                "depends_on": [],
            })

        if any(kw in user_message.lower() for kw in ["分析", "analyze", "数据", "data"]):
            subtasks.append({
                "index": 1,
                "type": "analysis",
                "description": "数据分析",
                "assigned_model": self._select_best_model_for_capability({"chat", "reasoning"}),
                "priority": 2,
                "depends_on": [],
            })

        if any(kw in user_message.lower() for kw in ["总结", "summarize", "概括"]):
            subtasks.append({
                "index": 2,
                "type": "synthesis",
                "description": "综合总结",
                "assigned_model": self._select_best_model_for_capability({"chat"}),
                "priority": 3,
                "depends_on": [0, 1] if len(subtasks) >= 2 else [],
            })

        # 如果没有匹配到特定任务，创建一个通用的推理任务
        if not subtasks:
            subtasks.append({
                "index": 0,
                "type": "reasoning",
                "description": "深度推理和分析",
                "assigned_model": self._select_best_model_for_capability({"chat", "reasoning"}),
                "priority": 1,
                "depends_on": [],
            })

        return CollaborationPlan(
            original_task=user_message,
            subtasks=subtasks,
            aggregation_strategy="sequential" if len(subtasks) > 1 else "parallel",
            estimated_cost=sum(
                self._get_model_cost(m.provider, m.model_name) 
                for m in [st["assigned_model"] for st in subtasks]
            ),
            reasoning="使用默认分解策略",
        )

    def _select_best_model_for_capability(self, required_caps: set[str]) -> ModelInfo:
        """为指定能力选择最佳模型"""
        candidates = [
            m for m in self.models
            if required_caps.issubset(m.capabilities) and m.is_available
        ]

        if not candidates:
            # 降级：选择任意可用模型
            candidates = [m for m in self.models if m.is_available]

        if not candidates:
            raise RuntimeError("没有可用的模型")

        # 按优先级和成本排序
        candidates.sort(key=lambda m: (m.priority, m.cost_per_1k))
        return candidates[0]

    async def _execute_subtasks(
        self,
        plan: CollaborationPlan,
        original_messages: list[dict],
    ) -> List[SubTaskResult]:
        """
        执行子任务 - 支持并行和串行执行

        根据依赖关系确定执行顺序：
        - 无依赖的子任务可以并行执行
        - 有依赖的子任务按依赖顺序执行
        """
        results: List[SubTaskResult] = []
        completed_indices: set[int] = set()

        # 按优先级排序
        sorted_subtasks = sorted(plan.subtasks, key=lambda st: st["priority"])

        for subtask in sorted_subtasks:
            # 等待依赖完成
            if subtask["depends_on"]:
                for dep_idx in subtask["depends_on"]:
                    if dep_idx not in completed_indices:
                        # 找到并等待依赖任务
                        dep_result = next(
                            (r for r in results if r.metadata.get("subtask_index") == dep_idx),
                            None,
                        )
                        if dep_result is None:
                            logger.warning(f"依赖任务 {dep_idx} 未完成，跳过当前任务")
                            continue

            # 执行子任务
            result = await self._execute_single_subtask(subtask, original_messages, results)
            results.append(result)
            completed_indices.add(subtask["index"])

        return results

    async def _execute_single_subtask(
        self,
        subtask: Dict[str, Any],
        original_messages: list[dict],
        previous_results: List[SubTaskResult],
    ) -> SubTaskResult:
        """执行单个子任务"""
        model_info = subtask["assigned_model"]
        subtask_type = SubTaskType(subtask["type"])

        # 构建子任务消息
        subtask_messages = self._build_subtask_messages(subtask, original_messages, previous_results)

        start_time = time.time()

        try:
            payload = {
                "model": model_info.model_name,
                "messages": subtask_messages,
                "temperature": 0.7 if subtask_type != SubTaskType.VERIFICATION else 0.3,
                "max_tokens": 4096,
            }

            client = await self._get_http_client()
            resp = await client.post(
                model_info.endpoint,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {model_info.api_key}",
                },
            )
            resp.raise_for_status()
            data = resp.json()

            execution_time = (time.time() - start_time) * 1000
            choice = data["choices"][0]
            usage = data.get("usage", {})

            return SubTaskResult(
                subtask_type=subtask_type,
                model_provider=model_info.provider,
                model_name=model_info.model_name,
                content=choice["message"]["content"],
                confidence=0.85,  # 默认置信度
                execution_time_ms=execution_time,
                metadata={
                    "subtask_index": subtask["index"],
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
            )

        except Exception as e:
            logger.error(f"子任务执行失败 [{subtask_type.value}]: {e}")
            execution_time = (time.time() - start_time) * 1000

            return SubTaskResult(
                subtask_type=subtask_type,
                model_provider=model_info.provider,
                model_name=model_info.model_name,
                content=f"[错误] 子任务执行失败: {str(e)}",
                confidence=0.0,
                execution_time_ms=execution_time,
                metadata={"error": str(e)},
            )

    def _build_subtask_messages(
        self,
        subtask: Dict[str, Any],
        original_messages: list[dict],
        previous_results: List[SubTaskResult],
    ) -> list[dict]:
        """构建子任务的对话消息"""
        system_prompts = {
            SubTaskType.RETRIEVAL: "你是信息检索专家，擅长查找和提取关键事实。",
            SubTaskType.REASONING: "你是逻辑推理专家，擅长分析和推导。",
            SubTaskType.ANALYSIS: "你是数据分析专家，擅长发现模式和趋势。",
            SubTaskType.SYNTHESIS: "你是综合总结专家，擅长整合多源信息。",
            SubTaskType.CREATION: "你是创意专家，擅长生成新颖的想法和方案。",
            SubTaskType.VERIFICATION: "你是验证专家，擅长检查正确性和一致性。",
            SubTaskType.CODING: "你是编程专家，擅长编写高质量代码。",
        }

        subtask_type = SubTaskType(subtask["type"])
        system_prompt = system_prompts.get(subtask_type, "你是AI助手。")

        # 添加之前子任务的结果作为上下文
        context = ""
        if previous_results:
            context = "\n\n相关上下文:\n"
            for prev in previous_results:
                if prev.confidence > 0.5:
                    context += f"[{prev.subtask_type.value}] {prev.content[:300]}...\n"

        user_content = f"""
原始任务: {original_messages[-1]['content'] if original_messages else ''}

当前子任务 ({subtask['type']}):
{subtask['description']}
{context}

请专注完成当前子任务。
"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

    async def _aggregate_results(
        self,
        plan: CollaborationPlan,
        subtask_results: List[SubTaskResult],
        original_messages: list[dict],
    ) -> AggregatedResult:
        """
        结果聚合器 - 整合多个子任务的结果

        聚合策略:
        1. sequential: 按顺序串联结果
        2. parallel: 并行结果合并
        3. voting: 投票机制（对同一问题的多个答案进行选择）
        """
        start_time = time.time()

        # 选择聚合模型（使用高优先级模型）
        aggregator_model = self._select_best_model_for_capability({"chat", "reasoning"})

        # 构建聚合提示
        aggregation_prompt = self._build_aggregation_prompt(plan, subtask_results, original_messages)

        try:
            client = await self._get_http_client()
            resp = await client.post(
                aggregator_model.endpoint,
                json={
                    "model": aggregator_model.model_name,
                    "messages": [
                        {"role": "system", "content": "你是结果聚合专家，擅长整合多个AI模型的输出。"},
                        {"role": "user", "content": aggregation_prompt},
                    ],
                    "temperature": 0.5,
                    "max_tokens": 4096,
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {aggregator_model.api_key}",
                },
            )
            resp.raise_for_status()
            data = resp.json()

            final_response = data["choices"][0]["message"]["content"]
            aggregation_time = (time.time() - start_time) * 1000

            # 计算总成本和时间
            total_cost = sum(
                self._get_model_cost(r.model_provider, r.model_name) *
                (r.metadata.get("total_tokens", 0) / 1000)
                for r in subtask_results
            )
            total_time = sum(r.execution_time_ms for r in subtask_results) + aggregation_time

            models_used = list(set(
                f"{r.model_provider}/{r.model_name}" for r in subtask_results
            ))

            collaboration_summary = (
                f"🤝 多模型协作完成\n"
                f"   • 子任务数: {len(subtask_results)}\n"
                f"   • 使用模型: {', '.join(models_used)}\n"
                f"   • 总耗时: {total_time:.0f}ms\n"
                f"   • 预估成本: ${total_cost:.4f}"
            )

            return AggregatedResult(
                final_response=final_response,
                subtask_results=subtask_results,
                collaboration_summary=collaboration_summary,
                total_cost=total_cost,
                total_time_ms=total_time,
                models_used=models_used,
            )

        except Exception as e:
            logger.error(f"结果聚合失败: {e}，使用简单拼接策略")
            return self._simple_aggregation(plan, subtask_results)

    def _build_aggregation_prompt(
        self,
        plan: CollaborationPlan,
        subtask_results: List[SubTaskResult],
        original_messages: list[dict],
    ) -> str:
        """构建聚合提示"""
        prompt = f"""
原始任务: {plan.original_task}

以下是多个专业模型完成的子任务结果：

"""
        for i, result in enumerate(subtask_results):
            prompt += f"""
--- 子任务 {i+1} ({result.subtask_type.value}) ---
模型: {result.model_provider}/{result.model_name}
置信度: {result.confidence:.2f}
结果:
{result.content}

"""

        prompt += """
请将以上多个子任务的结果整合为一个连贯、完整、高质量的最终回答。

要求:
1. 保持逻辑清晰，结构合理
2. 去除重复和矛盾的信息
3. 突出关键结论和建议
4. 语言流畅自然
5. 如果子任务结果有冲突，基于置信度和专业性进行判断

最终回答:
"""
        return prompt

    def _simple_aggregation(
        self,
        plan: CollaborationPlan,
        subtask_results: List[SubTaskResult],
    ) -> AggregatedResult:
        """简单聚合策略（当 AI 聚合失败时使用）"""
        # 按子任务类型分组
        sections = []
        for result in subtask_results:
            sections.append(f"## {result.subtask_type.value.upper()}\n\n{result.content}\n")

        final_response = "\n".join(sections)

        total_cost = sum(
            self._get_model_cost(r.model_provider, r.model_name) * 
            (r.metadata.get("total_tokens", 0) / 1000)
            for r in subtask_results
        )
        total_time = sum(r.execution_time_ms for r in subtask_results)

        models_used = list(set(
            f"{r.model_provider}/{r.model_name}" for r in subtask_results
        ))

        return AggregatedResult(
            final_response=final_response,
            subtask_results=subtask_results,
            collaboration_summary=f"简单聚合: {len(subtask_results)} 个子任务",
            total_cost=total_cost,
            total_time_ms=total_time,
            models_used=models_used,
        )


# 全局单例
ai_router = AIRouter()
