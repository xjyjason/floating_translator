# 悬浮翻译助手（Floating Translator）

一个基于 PySide6 的桌面悬浮翻译工具，使用百度翻译开放接口，实现：

- 悬浮球快速唤起主窗口
- 文本框输入并翻译
- 一键从剪贴板读取并翻译
- 系统托盘图标控制显示/隐藏与退出

## 功能概览

- 支持中英互译，自动检测源语言：
  - 自动检测 → 中文
  - 自动检测 → 英文
  - 英文 → 中文
  - 中文 → 英文
- 悬浮球始终置顶，可拖拽移动，点击切换主窗口显示
- 翻译失败时弹出错误提示

## 目录结构

```text
floating_translator/
├─ app.py                   # 主程序入口（UI 与逻辑）
├─ Baidu_Text_transAPI.py   # 百度文本翻译 API 封装
├─ build_exe.bat            # 使用 PyInstaller 打包为 exe
├─ logo/                    # 程序图标资源
└─ .gitignore
```

## 环境要求

- 操作系统：Windows
- Python：3.x（建议 3.8 及以上）
- 依赖库：
  - PySide6
  - requests
  - （可选）pyinstaller（用于打包）

## 安装依赖

在项目根目录下执行：

```bash
pip install PySide6 requests
```

如需打包为独立 exe，可额外安装：

```bash
pip install pyinstaller
```

## 配置百度翻译密钥

翻译功能依赖百度通用翻译 API。请在使用前：

1. 注册并登录百度翻译开放平台，创建应用，获取 `appid` 和 `appkey`
2. 打开 `Baidu_Text_transAPI.py`
3. 将文件中的 `appid` 和 `appkey` 替换为你自己的密钥

> 建议在实际项目中避免把密钥直接写入代码仓库，可根据需要改为读取环境变量或本地配置文件。

## 运行项目

在项目根目录执行：

```bash
python app.py
```

启动后：

- 会先显示一个悬浮球
- 单击悬浮球可打开主窗口
- 主窗口中可以：
  - 在“输入文本”中输入待翻译内容，点击“翻译”
  - 点击“剪贴板翻译”直接翻译当前剪贴板文本
  - 点击“收起为悬浮球”隐藏主窗口，仅保留悬浮球

任务栏托盘菜单中可：

- 显示主窗口
- 显示悬浮球
- 退出程序

## 打包为 Windows 可执行文件

项目提供了简单的打包脚本 [`build_exe.bat`](build_exe.bat)：

1. 确保已经安装 `pyinstaller`
2. 在项目根目录双击运行 `build_exe.bat`，或在命令行执行：

   ```bash
   build_exe.bat
   ```

脚本会：

- 清理旧的 `build/` 与 `dist/` 目录
- 重新生成 `FloatingTranslator.spec`
- 使用图标 `logo/translater.ico` 打包 `app.py`
- 在 `dist/FloatingTranslator/` 目录下生成可执行文件

## 注意事项

- 请妥善保管和使用自己的百度翻译密钥，避免泄露
- 若遇到网络错误或接口返回错误，程序会在界面中弹出提示

