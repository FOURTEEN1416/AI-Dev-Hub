"""验证 AI 提取管道模块导入"""
import sys
sys.path.insert(0, r"C:\Users\FOUR\Desktop\爬虫工具\ai-dev-hub\spiders")

from spiders.config import settings
print(f"ENABLE_AI_EXTRACT: {settings.ENABLE_AI_EXTRACT}")

from spiders.pipeline import DataPipeline, _AI_AVAILABLE
print(f"_AI_AVAILABLE: {_AI_AVAILABLE}")

from spiders.models import OpportunityItem
print(f"OpportunityItem fields: {list(OpportunityItem.model_fields.keys())}")

print("All imports OK")
