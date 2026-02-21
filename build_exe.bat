@echo off
setlocal

cd /d "%~dp0"

echo 清理旧的 build 和 dist 目录...
if exist build rd /s /q build
if exist dist rd /s /q dist

echo 删除旧的 spec 文件（如存在）...
if exist FloatingTranslator.spec del /q FloatingTranslator.spec

echo 重新生成 spec 并打包为 exe...
pyinstaller ^
  --noconsole ^
  --name FloatingTranslator ^
  --icon logo\translater.ico ^
  --add-data "logo;logo" ^
  app.py

echo.
echo 打包完成，输出目录为 dist\FloatingTranslator
pause

endlocal

