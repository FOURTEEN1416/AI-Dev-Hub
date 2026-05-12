"""验证所有爬虫模块可导入"""
from spiders.github.trending import GitHubTrendingSpider
print('github OK')
from spiders.hackernews.hot import HackerNewsSpider
print('hackernews OK')
from spiders.competitions.kaggle import KaggleSpider
print('kaggle OK')
from spiders.competitions.tianchi import TianchiSpider
print('tianchi OK')
from spiders.developer_programs.openai import OpenAISpider
print('openai OK')
from spiders.forums.v2ex import V2exSpider
print('v2ex OK')
from spiders.forums.juejin import JuejinSpider
print('juejin OK')
print('All OK!')
