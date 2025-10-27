#!/bin/bash

echo "====================================="
echo "XGBoost 训练脚本 - 快速启动"
echo "====================================="
echo

echo "[1/3] 激活conda环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate jiugang
if [ $? -ne 0 ]; then
    echo "错误: 无法激活jiugang环境"
    echo "请先运行: conda create -n jiugang python=3.10 -y"
    exit 1
fi

echo "[2/3] 检查依赖..."
python -c "import yaml, pandas, xgboost" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "依赖不完整，正在安装..."
    pip install -r requirements.txt
else
    echo "依赖已安装 ✓"
fi

echo
echo "[3/3] 选择运行模式:"
echo
echo "1. 快速测试 (10次试验，约5分钟)"
echo "2. 正式训练 (100次试验，约30-60分钟)"
echo "3. 回归模式 (100次试验，约30-60分钟)"
echo "4. 自定义配置"
echo

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo
        echo "运行快速测试..."
        python main.py --config config_quick_test.yaml
        ;;
    2)
        echo
        echo "运行正式训练（分类模式）..."
        python main.py
        ;;
    3)
        echo
        echo "运行回归模式..."
        python main.py --config config_regression.yaml
        ;;
    4)
        read -p "请输入配置文件路径: " config_file
        echo
        echo "运行自定义配置..."
        python main.py --config $config_file
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo
echo "====================================="
echo "训练完成！"
echo "====================================="
echo
echo "查看输出目录获取结果"

