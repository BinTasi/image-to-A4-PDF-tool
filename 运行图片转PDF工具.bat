@echo off
cls
echo 正在启动批量图片转PDF工具...
echo ==================================
echo 请稍候，程序正在初始化...
echo 转换完成后会显示保存路径
echo ==================================
echo.
:: 使用命令行模式运行可执行文件，避免窗口模式下的stdin错误
dist\batch_images_to_a4_pdf_with_logging.exe
echo.
echo 程序运行完毕！
echo 请按任意键关闭窗口...
pause >nul