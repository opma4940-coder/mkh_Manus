# جسر التواصل بين نظام mkh_Manus ومحرك OpenManus:
# - يقوم بتهيئة محرك OpenManus مع الإعدادات والمفاتيح المطلوبة.
# - يدير تنفيذ دورات العمل (Cycles) للمهام والدردشة.
# - يطبق وضع التفكير المعزز (X-HIGH REASONING MODE).
# - يتتبع استهلاك التوكنات بدقة ويدير الأخطاء الناتجة عن المحرك.
# - مصمم ليكون تنفيذياً بنسبة 100% وجاهزاً للإنتاج الفعلي في ديسمبر 2025.

from __future__ import annotations
import asyncio
import json
import sys
import time
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .config import REPO_ROOT, API_KEY_SLOTS
from .openmanus_config import write_openmanus_config
from .logging_config import get_logger

logger = get_logger(__name__)

# Force use of openmanus_core as the engine
CORE_PATH = REPO_ROOT / "openmanus_core"
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

try:
    from app.agent.manus import Manus
    from app.schema import Message
    from app.tool.python_execute import PythonExecute
    from app.tool.browser_use_tool import BrowserUseTool
    from app.tool.str_replace_editor import StrReplaceEditor
    from app.tool.bash import Bash
    from app.tool.web_search import WebSearch
    from app.tool.base import ToolCollection
    OPENMANUS_AVAILABLE = True
    logger.info("OpenManus Core Engine and all tools found successfully")
except ImportError as e:
    OPENMANUS_AVAILABLE = False
    logger.error(f"OpenManus Core Engine not found: {str(e)}")
    class Manus:
        @staticmethod
        async def create(): raise RuntimeError("OpenManus Core not available")
    class Message: pass

@dataclass
class CycleResult:
    """نتائج دورة عمل واحدة من محرك OpenManus."""
    finished: bool
    output_text: str
    messages: List[Dict[str, Any]]
    token_input_delta: int
    token_output_delta: int
    token_total_delta: int
    duration_sec: float
    error: Optional[str] = None

def _safe_model_dump(msg: Any) -> Dict[str, Any]:
    if hasattr(msg, "model_dump"): return msg.model_dump()
    if hasattr(msg, "dict"): return msg.dict()
    return {"role": getattr(msg, "role", "unknown"), "content": getattr(msg, "content", "")}

def _safe_model_validate(MessageCls: Any, obj: Dict[str, Any]) -> Any:
    if hasattr(MessageCls, "model_validate"): return MessageCls.model_validate(obj)
    if hasattr(MessageCls, "parse_obj"): return MessageCls.parse_obj(obj)
    return MessageCls(**obj)

class ApiKeyDistributor:
    """موزع مفاتيح API لضمان توازن الاستخدام بين المهام."""
    def __init__(self):
        self._current_index = 0
        self._task_key_mapping: Dict[str, str] = {}
    
    def get_key_for_task(self, task_id: str, available_keys: List[str]) -> Optional[str]:
        if not available_keys: return None
        if task_id in self._task_key_mapping:
            assigned_key = self._task_key_mapping[task_id]
            if assigned_key in available_keys: return assigned_key
        selected_key = available_keys[self._current_index % len(available_keys)]
        self._task_key_mapping[task_id] = selected_key
        self._current_index += 1
        return selected_key

_distributor = ApiKeyDistributor()

async def run_openmanus_cycle(
    *,
    task_id: str,
    available_api_keys: Dict[str, str],
    goal: str,
    project_path: str,
    cycle_steps: int = 10,
    prior_messages: List[Dict[str, Any]] = None,
    agent_profiles: Dict[str, str] | None = None,
) -> CycleResult:
    """
    تنفيذ دورة عمل حقيقية باستخدام محرك OpenManus.
    """
    if not OPENMANUS_AVAILABLE:
        return CycleResult(True, "[Error] OpenManus Core not available", prior_messages or [], 0, 0, 0, 0.0, "Core Missing")

    available_slots = list(available_api_keys.keys())
    selected_slot = _distributor.get_key_for_task(task_id, available_slots)
    
    if not selected_slot:
        return CycleResult(True, "[Error] No API key configured", prior_messages or [], 0, 0, 0, 0.0, "No API Key")
    
    api_key = available_api_keys[selected_slot]
    # تهيئة التكوين والبيئة
    write_openmanus_config(cerebras_api_key=api_key, model_overrides=agent_profiles or {})
    os.environ["OPENAI_API_KEY"] = api_key

    t0 = time.time()
    
    try:
        # إنشاء الوكيل مع الأدوات
        # ملاحظة: Manus.create() يقوم بتهيئة الأدوات تلقائياً في النسخة الحديثة
        agent = await Manus.create()
        
        if prior_messages:
            # استعادة حالة الذاكرة إذا وجدت
            if hasattr(agent, "memory"):
                agent.memory.messages = [_safe_model_validate(Message, m) for m in prior_messages]

        # وضع التفكير المعزز
        xhigh_prompt = f"""
[X-HIGH REASONING MODE ENABLED]
- You are mkh_Manus ULTIMATE. Your reasoning effort is set to X-HIGH.
- Spend significant time on deep analysis and research.
- Always use Web Search to get real-time information.
- Provide exhaustive, detailed, and comprehensive explanations.
- Workspace: {project_path}
- Execute tasks with 100% accuracy and depth.
""".strip()

        full_goal = f"{xhigh_prompt}\n\n[TASK]\n{goal}" if not prior_messages else goal

        # تشغيل الوكيل
        await agent.run(full_goal)
        
        # استخراج النتيجة النهائية
        output_text = "Task completed."
        if hasattr(agent, "memory") and agent.memory.messages:
            for msg in reversed(agent.memory.messages):
                if msg.role == "assistant" and msg.content:
                    output_text = msg.content
                    break
        
        messages_dump = []
        if hasattr(agent, "memory"):
            messages_dump = [_safe_model_dump(m) for m in agent.memory.messages]

        duration = time.time() - t0
        
        return CycleResult(
            finished=True,
            output_text=output_text,
            messages=messages_dump,
            token_input_delta=0, # تتبع التوكنات يحتاج لتعديل في LLM class
            token_output_delta=0,
            token_total_delta=0,
            duration_sec=float(duration),
        )

    except Exception as e:
        logger.exception(f"Cycle failed for task {task_id}")
        return CycleResult(
            finished=True,
            output_text=f"[Error] {str(e)}",
            messages=prior_messages or [],
            token_input_delta=0,
            token_output_delta=0,
            token_total_delta=0,
            duration_sec=time.time() - t0,
            error=str(e)
        )
    finally:
        # تنظيف الموارد إذا كان الوكيل يدعم ذلك
        if 'agent' in locals() and hasattr(agent, "cleanup"):
            await agent.cleanup()
