#!/bin/bash

echo "====================================="
echo "清理Git中不应该追踪的文件"
echo "====================================="
echo

echo "正在移除已追踪但应该被忽略的文件..."
echo

# 移除PyCharm配置
echo "[1/6] 移除PyCharm配置..."
git rm -r --cached .idea/ 2>/dev/null
git rm --cached *.iml 2>/dev/null

# 移除VSCode配置
echo "[2/6] 移除VSCode配置..."
git rm -r --cached .vscode/ 2>/dev/null

# 移除Python缓存
echo "[3/6] 移除Python缓存..."
git rm -r --cached xgboost_trainer/__pycache__/ 2>/dev/null
git rm --cached xgboost_trainer/*.pyc 2>/dev/null

# 移除输出目录
echo "[4/6] 移除输出目录..."
git rm -r --cached xgboost_trainer/output*/ 2>/dev/null
git rm -r --cached xgboost_trainer/plots*/ 2>/dev/null
git rm -r --cached xgboost_trainer/plot_*/ 2>/dev/null

# 移除模型文件
echo "[5/6] 移除模型文件..."
git rm --cached xgboost_trainer/*.pkl 2>/dev/null
git rm --cached xgboost_trainer/*.json 2>/dev/null
git rm --cached xgboost_trainer/output*/*.json 2>/dev/null

# 移除数据文件（如果你注释掉了.gitignore中的规则，可以跳过）
echo "[6/6] 移除数据文件..."
# git rm --cached xgboost_trainer/data_realtime/*.csv 2>/dev/null
# git rm --cached xgboost_trainer/data_ahead/*.csv 2>/dev/null

echo
echo "====================================="
echo "清理完成！"
echo "====================================="
echo
echo "现在查看状态："
git status

echo
echo "如果看到删除的文件，请运行："
echo "git commit -m 'chore: 清理不应该追踪的文件'"
echo

