# توليد config/config.toml الخاص بـ OpenManus ديناميكياً من السيرفر.
#
# لماذا؟
# - لأنك طلبت أن API Key لا يُكتب في السكربت ولا يُوضع يدوياً في ملفات المشروع.
# - لذلك: المستخدم يضع Cerebras API Key عبر Dashboard -> Backend يخزنه مشفراً
#   ثم يولد config/config.toml عند الحاجة لتشغيل محرك OpenManus.
#
# كيف؟
# - نكتب ملف TOML عملي (محدود وبسيط) كحد أدنى مطلوب لتشغيل OpenManus.

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

from .config import CEREBRAS_BASE_URL_DEFAULT, DEFAULT_AGENT_PROFILES, OPENMANUS_CONFIG_PATH

def write_openmanus_config(
    cerebras_api_key: str,
    model_overrides: Dict[str, str] | None = None,
) -> Path:
    """
    يكتب/يحدّث config/config.toml داخل مستودع OpenManus.

    model_overrides:
      dict مثل {"planner_model":"...", "coder_model":"..."} لتغيير خريطة الوكلاء.
    """
    model_overrides = model_overrides or {}
    base_url = os.getenv("CEREBRAS_BASE_URL", CEREBRAS_BASE_URL_DEFAULT)

    planner = model_overrides.get("planner_model", DEFAULT_AGENT_PROFILES.planner_model)
    researcher = model_overrides.get("researcher_model", DEFAULT_AGENT_PROFILES.researcher_model)
    coder = model_overrides.get("coder_model", DEFAULT_AGENT_PROFILES.coder_model)
    auditor = model_overrides.get("auditor_model", DEFAULT_AGENT_PROFILES.auditor_model)
    summarizer = model_overrides.get("summarizer_model", DEFAULT_AGENT_PROFILES.summarizer_model)

    # ملاحظة مهمة:
    # OpenManus يستخدم "api_type" في بعض الإعدادات. سنضبطه openai لأنه OpenAI-compatible.
    toml = f"""
# هذا الملف يتم توليده تلقائياً بواسطة Manus-Pro Backend.
# لا تقم بتخزينه في Git. (تم تضمينه في .gitignore)
#
# الهدف:
# ربط OpenManus بمحرك Cerebras (OpenAI-compatible) وفق نماذج خطتك المجانية.

[llm]
api_type = "openai"
model = "{planner}"
base_url = "{base_url}"
api_key = "{cerebras_api_key}"
max_tokens = 4096
temperature = 0.0

# ملفات/أقسام اختيارية للوكلاء (Profiles):
# ملاحظة: OpenManus يقوم بإنشاء LLM(config_name=<agent_name_lower>).
# لذا نضيف أقساماً بأسماء عامة يمكن استخدامها داخل طبقاتنا.
[llm.planner]
api_type = "openai"
model = "{planner}"
base_url = "{base_url}"
api_key = "{cerebras_api_key}"
max_tokens = 4096
temperature = 0.0

[llm.researcher]
api_type = "openai"
model = "{researcher}"
base_url = "{base_url}"
api_key = "{cerebras_api_key}"
max_tokens = 4096
temperature = 0.2

[llm.coder]
api_type = "openai"
model = "{coder}"
base_url = "{base_url}"
api_key = "{cerebras_api_key}"
max_tokens = 4096
temperature = 0.1

[llm.auditor]
api_type = "openai"
model = "{auditor}"
base_url = "{base_url}"
api_key = "{cerebras_api_key}"
max_tokens = 4096
temperature = 0.0

[llm.summarizer]
api_type = "openai"
model = "{summarizer}"
base_url = "{base_url}"
api_key = "{cerebras_api_key}"
max_tokens = 2048
temperature = 0.0

# تشغيل متعدد الوكلاء (اختياري في OpenManus)
[runflow]
use_data_analysis_agent = true
""".lstrip()

    OPENMANUS_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    OPENMANUS_CONFIG_PATH.write_text(toml, encoding="utf-8")

    # حماية صلاحيات الملف (قدر الإمكان)
    try:
        os.chmod(OPENMANUS_CONFIG_PATH, 0o600)
    except Exception:
        pass

    return OPENMANUS_CONFIG_PATH
