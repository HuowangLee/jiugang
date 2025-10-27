# Git 快速参考

## 🚀 首次设置

```bash
# 进入项目根目录
cd D:\Projects\jiugang2

# 初始化Git仓库
git init

# 配置用户信息
git config user.name "你的名字"
git config user.email "your.email@example.com"

# 添加所有文件（.gitignore会自动排除不需要的文件）
git add .

# 查看即将提交的文件
git status

# 首次提交
git commit -m "初始提交：XGBoost训练脚本重构版"
```

## 📝 日常使用

### 查看状态
```bash
# 查看工作区状态
git status

# 查看修改内容
git diff

# 查看已暂存的修改
git diff --staged
```

### 提交更改
```bash
# 添加单个文件
git add config.yaml

# 添加多个文件
git add config.yaml main.py

# 添加所有修改过的文件
git add -u

# 提交
git commit -m "更新配置参数"

# 添加并提交（快捷方式）
git commit -am "修复数据加载bug"
```

### 查看历史
```bash
# 简洁历史
git log --oneline

# 详细历史
git log

# 图形化历史
git log --graph --oneline --all

# 查看某个文件的历史
git log -- config.yaml
```

## 🌿 分支操作

```bash
# 查看分支
git branch

# 创建新分支
git branch dev

# 切换分支
git checkout dev

# 创建并切换分支（快捷方式）
git checkout -b feature/new-model

# 合并分支
git checkout main
git merge dev

# 删除分支
git branch -d dev
```

## 🔄 撤销操作

```bash
# 撤销工作区的修改（文件未add）
git checkout -- filename.py

# 撤销已add的文件
git reset HEAD filename.py

# 撤销最后一次提交（保留修改）
git reset --soft HEAD^

# 撤销最后一次提交（丢弃修改）
git reset --hard HEAD^

# 修改最后一次提交信息
git commit --amend -m "新的提交信息"
```

## 🌐 远程仓库

```bash
# 添加远程仓库
git remote add origin https://github.com/username/repo.git

# 查看远程仓库
git remote -v

# 推送到远程
git push origin main

# 首次推送并设置上游
git push -u origin main

# 拉取远程更新
git pull origin main

# 克隆仓库
git clone https://github.com/username/repo.git
```

## 📦 标签管理

```bash
# 创建标签
git tag v1.0.0

# 创建带注释的标签
git tag -a v1.0.0 -m "版本1.0.0发布"

# 查看标签
git tag

# 查看标签信息
git show v1.0.0

# 推送标签到远程
git push origin v1.0.0

# 推送所有标签
git push origin --tags

# 删除标签
git tag -d v1.0.0
```

## 🔍 常用检查

```bash
# 查看被忽略的文件
git status --ignored

# 查看某个文件的修改历史
git log -p filename.py

# 查看谁修改了某行代码
git blame filename.py

# 搜索提交信息
git log --grep="bug"

# 搜索代码内容
git log -S "function_name"
```

## 💡 实用技巧

### 1. 暂存工作进度
```bash
# 暂存当前工作
git stash

# 查看暂存列表
git stash list

# 恢复暂存
git stash pop

# 恢复特定暂存
git stash apply stash@{0}
```

### 2. 比较差异
```bash
# 比较工作区和暂存区
git diff

# 比较暂存区和上次提交
git diff --staged

# 比较两个分支
git diff main dev

# 比较两个提交
git diff commit1 commit2
```

### 3. 清理操作
```bash
# 清理未跟踪的文件（预览）
git clean -n

# 清理未跟踪的文件
git clean -f

# 清理未跟踪的文件和目录
git clean -fd
```

## 📊 本项目常用命令

### 修改配置
```bash
git add config.yaml
git commit -m "config: 调整超参数搜索范围"
```

### 添加新功能
```bash
git add model_trainer.py
git commit -m "feat: 添加早停机制"
```

### 修复Bug
```bash
git add data_loader.py
git commit -m "fix: 修复CSV编码问题"
```

### 更新文档
```bash
git add README.md
git commit -m "docs: 更新使用说明"
```

### 批量提交
```bash
git add config.yaml main.py utils.py
git commit -m "refactor: 重构配置管理模块"
```

## ⚠️ 注意事项

1. **提交前检查**
   ```bash
   git status  # 确认要提交的文件
   git diff    # 检查修改内容
   ```

2. **不要提交的内容**
   - 数据文件（`.csv`, `.xlsx`）
   - 输出目录（`output*/`）
   - 模型文件（`.pkl`, `.json`）
   - 个人配置

3. **提交信息规范**
   - `feat:` 新功能
   - `fix:` Bug修复
   - `docs:` 文档更新
   - `style:` 代码格式
   - `refactor:` 重构
   - `test:` 测试
   - `chore:` 构建工具

## 🆘 常见问题

**Q: 如何撤销add操作？**
```bash
git reset HEAD filename
```

**Q: 如何放弃所有本地修改？**
```bash
git reset --hard HEAD
```

**Q: 如何查看某次提交的内容？**
```bash
git show commit_hash
```

**Q: 如何恢复已删除的文件？**
```bash
git checkout HEAD -- filename
```

**Q: 误提交了大文件怎么办？**
```bash
# 从历史中移除
git filter-branch --tree-filter 'rm -f large_file' HEAD
```

## 📚 更多资源

- 详细说明：查看 `Git管理说明.md`
- [Git官方文档](https://git-scm.com/doc)
- [GitHub指南](https://guides.github.com/)

---

**提示**: 养成频繁提交的习惯，每次只提交相关的修改。

