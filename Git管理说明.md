# Git 版本管理说明

## 📁 .gitignore 配置说明

本项目的 `.gitignore` 文件配置了以下忽略规则：

### ✅ 应该提交的文件

#### 核心代码
- ✅ `*.py` - 所有Python源代码
  - `main.py`
  - `config_manager.py`
  - `utils.py`
  - `data_loader.py`
  - `feature_engineering.py`
  - `model_trainer.py`
  - `evaluator.py`

#### 配置文件
- ✅ `config.yaml` - 默认配置
- ✅ `config_regression.yaml` - 回归配置示例
- ✅ `config_quick_test.yaml` - 快速测试配置
- ✅ `requirements.txt` - 依赖包列表

#### 文档
- ✅ `README.md` - 项目说明
- ✅ `使用指南.md` - 使用说明
- ✅ `重构说明.md` - 重构文档
- ✅ `项目文件清单.md` - 文件清单
- ✅ `Git管理说明.md` - 本文档

#### 脚本
- ✅ `快速开始.bat` - Windows启动脚本
- ✅ `快速开始.sh` - Linux/Mac启动脚本

### ❌ 应该忽略的文件

#### Python相关
- ❌ `__pycache__/` - Python缓存
- ❌ `*.pyc`, `*.pyo` - 字节码文件
- ❌ `*.egg-info/` - 包信息

#### 数据文件
- ❌ `*.csv` - 所有CSV数据文件
- ❌ `*.xlsx`, `*.xls` - Excel文件
- ❌ `data_*/` - 所有数据目录
  - `data_realtime/`
  - `data_ahead/`

#### 训练输出
- ❌ `output*/` - 所有输出目录
  - `output-20251026_143022/`
  - `output-base/`
  - `output-rmse线性加权/`
- ❌ `plots*/` - 图表目录
- ❌ `plot_*/` - 绘图目录

#### 模型文件
- ❌ `*.pkl` - Pickle模型
- ❌ `*.json` - JSON模型（除了配置文件）
- ❌ `*.joblib` - Joblib模型

#### 图表文件
- ❌ `*.png`, `*.jpg`, `*.pdf` - 图表图片

#### 临时文件
- ❌ `*.log` - 日志文件
- ❌ `*.tmp`, `*.bak` - 临时备份
- ❌ `.DS_Store`, `Thumbs.db` - 系统文件

#### IDE文件
- ❌ `.vscode/`, `.idea/` - IDE配置
- ❌ `*.swp`, `*.swo` - Vim临时文件

## 📝 Git 工作流建议

### 1. 初始化仓库

```bash
cd D:\Projects\jiugang2
git init
git add .
git commit -m "初始提交：XGBoost训练脚本重构版"
```

### 2. 分支管理

```bash
# 创建开发分支
git checkout -b dev

# 创建功能分支
git checkout -b feature/new-feature

# 合并到主分支
git checkout main
git merge dev
```

### 3. 日常提交

```bash
# 查看状态
git status

# 添加修改的文件
git add config.yaml
git add main.py

# 提交
git commit -m "更新配置文件，优化训练参数"

# 推送
git push origin main
```

### 4. 常用命令

```bash
# 查看忽略的文件
git status --ignored

# 强制添加被忽略的文件（如果确实需要）
git add -f some_data.csv

# 查看提交历史
git log --oneline

# 撤销未提交的修改
git checkout -- filename

# 查看差异
git diff
```

## 🎯 特殊情况处理

### 情况1: 需要提交小样本数据

如果需要提交少量示例数据用于测试：

```bash
# 1. 创建示例数据目录
mkdir xgboost_trainer/sample_data

# 2. 在 .gitignore 中添加例外
# 在 .gitignore 底部添加：
# !xgboost_trainer/sample_data/*.csv

# 3. 提交示例数据
git add xgboost_trainer/sample_data/
git commit -m "添加示例数据"
```

### 情况2: 需要保留某个特定的训练结果

```bash
# 1. 复制结果到专门目录
mkdir results_archive
cp -r xgboost_trainer/output-20251026_143022/ results_archive/best_result/

# 2. 在 .gitignore 中添加例外
# !results_archive/

# 3. 提交重要结果
git add results_archive/
git commit -m "保存最佳训练结果 (accuracy=0.95)"
```

### 情况3: 多人协作配置文件管理

```bash
# 1. 使用配置模板
cp config.yaml config_template.yaml

# 2. 将实际配置添加到 .gitignore
# 在 .gitignore 中添加：
# config_local.yaml
# config_private.yaml

# 3. 提交模板
git add config_template.yaml
git commit -m "添加配置文件模板"

# 4. 每个开发者创建自己的配置
cp config_template.yaml config_local.yaml
# 修改 config_local.yaml（不会被提交）
```

## 🔍 检查清单

提交代码前检查：

- [ ] 没有提交数据文件（`.csv`, `.xlsx`等）
- [ ] 没有提交输出目录（`output*/`）
- [ ] 没有提交模型文件（`.pkl`, `.json`）
- [ ] 没有提交个人配置（如果有的话）
- [ ] 没有提交IDE配置文件
- [ ] 代码已经过测试
- [ ] 提交信息清晰明确

## 📊 建议的提交信息格式

```bash
# 功能添加
git commit -m "feat: 添加新的特征工程模块"

# Bug修复
git commit -m "fix: 修复数据加载时的编码问题"

# 文档更新
git commit -m "docs: 更新使用指南"

# 性能优化
git commit -m "perf: 优化超参数搜索算法"

# 代码重构
git commit -m "refactor: 重构模型训练模块"

# 配置更改
git commit -m "config: 调整默认超参数"
```

## 🚨 注意事项

### ⚠️ 绝对不要提交的内容

1. **敏感数据**
   - 包含个人信息的数据
   - 商业机密数据
   - 密码和密钥

2. **大文件**
   - 超过50MB的文件
   - 原始数据集
   - 大型模型文件

3. **临时文件**
   - 中间结果
   - 调试输出
   - 日志文件

### ✅ 推荐做法

1. **数据管理**
   - 使用Git LFS管理大文件（如需要）
   - 在README中说明如何获取数据
   - 提供数据下载脚本

2. **配置管理**
   - 使用环境变量存储敏感信息
   - 提供配置模板
   - 在README中说明配置方法

3. **版本标签**
   - 对重要版本打标签
   - 使用语义化版本号
   ```bash
   git tag -a v1.0.0 -m "发布1.0.0版本"
   git push origin v1.0.0
   ```

## 📚 相关资源

- [Git官方文档](https://git-scm.com/doc)
- [gitignore模板](https://github.com/github/gitignore)
- [语义化版本](https://semver.org/lang/zh-CN/)

---

**建议**: 定期检查 `.gitignore` 是否正确工作，避免误提交大文件或敏感数据。

