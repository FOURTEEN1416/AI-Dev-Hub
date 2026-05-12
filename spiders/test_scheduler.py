"""验证 scheduler 适配升级"""
import sys
sys.path.insert(0, r"C:\Users\FOUR\Desktop\爬虫工具\ai-dev-hub\spiders")
from spiders.scheduler import create_scheduler
s = create_scheduler()
print(f"Registered: {s.list_spiders()}")
print(f"Engine: {s._engine_label}")
print("scheduler OK")
