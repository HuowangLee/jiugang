@echo off
chcp 65001 >nul
echo =====================================
echo XGBoost 训练脚本 - 快速启动
echo =====================================
echo.

echo [1/3] 激活conda环境...
call conda activate jiugang
if errorlevel 1 (
    echo 错误: 无法激活jiugang环境
    echo 请先运行: conda create -n jiugang python=3.10 -y
    pause
    exit /b 1
)

echo [2/3] 检查依赖...
python -c "import yaml, pandas, xgboost" 2>nul
if errorlevel 1 (
    echo 依赖不完整，正在安装...
    pip install -r requirements.txt
) else (
    echo 依赖已安装 ✓
)

echo.
echo [3/3] 选择运行模式:
echo.
echo 1. 快速测试 (10次试验，约5分钟)
echo 2. 正式训练 (100次试验，约30-60分钟)
echo 3. 回归模式 (100次试验，约30-60分钟)
echo 4. 自定义配置
echo.

set /p choice="请选择 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 运行快速测试...
    python main.py --config config_quick_test.yaml
) else if "%choice%"=="2" (
    echo.
    echo 运行正式训练（分类模式）...
    python main.py
) else if "%choice%"=="3" (
    echo.
    echo 运行回归模式...
    python main.py --config config_regression.yaml
) else if "%choice%"=="4" (
    set /p config_file="请输入配置文件路径: "
    echo.
    echo 运行自定义配置...
    python main.py --config %config_file%
) else (
    echo 无效选择
    pause
    exit /b 1
)

echo.
echo =====================================
echo 训练完成！
echo =====================================
echo.
echo 查看输出目录获取结果
pause

