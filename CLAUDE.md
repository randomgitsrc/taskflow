# Claude Code 配置

## 禁用 Thinking 模式

当前项目使用 OmniRouter + Kimi K2.5，该组合不支持 thinking 模式的 reasoning_content 字段。

请在当前会话中：
- 禁用 thinking 模式
- 使用普通 chat completion 模式
- 不要触发 thinking 或 reasoning 相关的 API 调用

## 原因
Kimi K2.5 不返回 reasoning_content 字段，会导致 API 400 错误。
