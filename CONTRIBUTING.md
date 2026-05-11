# 贡献指南

感谢您考虑为AI开发者机会聚合平台做出贡献！

## 如何贡献

### 报告Bug
请使用GitHub Issues提交bug报告。在提交之前，请确保：
- 搜索现有的Issues，确认该bug尚未被报告
- 使用Bug报告模板，提供尽可能详细的信息
- 包含复现步骤、期望行为和实际行为

### 提交功能请求
请使用GitHub Issues提交功能请求。在提交之前，请确保：
- 清晰描述您希望添加的功能
- 说明该功能要解决的问题
- 如果可能，提供实现建议

### 提交代码
1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 代码风格
- **Python**: 遵循PEP 8规范
- **TypeScript**: 使用ESLint配置
- **提交信息**: 使用约定式提交（Conventional Commits）

## 测试
请确保所有测试通过后再提交PR：
- 后端测试: `cd backend && pytest`
- 前端测试: `cd frontend && npm test`

## 代码审查
所有PR都需要至少一位维护者的审查。我们会尽快处理您的PR。

## 许可证
通过提交代码，您同意您的贡献将根据本项目的许可证进行授权。
