# UCAS慕课自动完成工具

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个自动化工具，用于完成国科大（UCAS）慕课平台的在线课程任务。

## 功能特点

- 🚀 自动完成慕课视频观看
- 📝 自动化课程任务处理
- 🔒 安全的登录机制
- ⚡ 高效的任务执行
- 🛠 可配置的运行参数

## 环境要求

- Python 3.7+
- Chrome浏览器
- ChromeDriver
- Selenium WebDriver

## 安装步骤

1. 克隆仓库到本地：
```bash
git clone https://github.com/onglu1/UCAS_auto_mooc.git
cd UCAS_auto_mooc
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境：
- 确保已安装Chrome浏览器
- 下载对应版本的ChromeDriver并添加到系统PATH中
- 确保Python环境变量配置正确

## 使用方法

1. 配置账号信息：
在main.py同层下创建 `config.json` 文件并按以下格式配置：
```json
{
   username = "你的用户名",
   password = "你的密码",
   course_url = "课程章节目录链接" // 进入课程主页，点击章节，复制链接
}
```
2. 运行程序：
```bash
python main.py
```

## 注意事项

- 请合理使用，遵守学校相关规定
- 建议在使用过程中保持网络稳定
- 使用前请确保账号密码正确
- 建议在非高峰时段运行程序
- 如遇到验证码问题，请手动处理

## 常见问题

1. ChromeDriver版本不匹配：
   - 请确保ChromeDriver版本与您的Chrome浏览器版本相匹配
   
2. 登录失败：
   - 检查账号密码是否正确
   - 确认网络连接是否稳定
   - 查看是否需要进行验证码处理

## 贡献指南

欢迎提交问题和合并请求。对于重大更改，请先开issue讨论您想要更改的内容。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 作者

- [@onglu1](https://github.com/onglu1)

## 更新日志

- 2024-03-17：项目初始化
- 添加基础自动化功能
- 实现视频/pdf自动观看
- 优化运行稳定性

## 免责声明

本工具仅供学习研究使用，请勿用于其他用途。使用本工具所产生的一切后果由使用者自行承担。

## 致谢

感谢所有为本项目提供建议和帮助的贡献者。
