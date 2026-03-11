# 快速开始指南

## 1?? 环境准备

### 创建虚拟环境（推荐）
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 安装依赖
```bash
pip install -r requirements.txt
```

---

## 2?? 配置环境变量

### 复制示例配置
```bash
copy .env.example .env  # Windows
# 或
cp .env.example .env    # Linux/Mac
```

### 编辑 .env 文件
**必填项**：
```env
OPENAI_API_KEY=sk-proj-xxxxx
```

**可选项**（如果用国内 API）：
```env
# 通义千问
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_API_KEY=sk-xxxxx
MODEL_NAME=qwen-plus

# 智谱 AI
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
OPENAI_API_KEY=xxxxx
MODEL_NAME=glm-4-plus
```

---

## 3?? 验证安装

### 测试 Python 环境
```bash
python -c "import langgraph; print(langgraph.__version__)"
```

### 测试配置加载
```bash
python -c "from intentrouter.config import settings; print(settings.model_name)"
```

---

## 4?? 开始 Phase 1

阅读并跟随 `PHASE1_GUIDE.md` 开始编写你的第一个 LangGraph！

---

## ? 遇到问题？

### 问题 1: pip 安装很慢
**解决**：使用国内镜像
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 2: 找不到模块
**确认**：
1. 虚拟环境已激活（命令行前有 `(.venv)` 标记）
2. 在项目根目录运行命令

### 问题 3: OPENAI_API_KEY 无效
**检查**：
1. `.env` 文件在项目根目录
2. 没有多余的引号：`OPENAI_API_KEY=sk-xxx`（不是 `"sk-xxx"`）
3. 重启 Python 进程加载新配置

---

## ? 项目结构一览

```
intentrouter-pro/
├── intentrouter/          # ? 你的代码写在这里
│   ├── graph/            # LangGraph 相关
│   ├── api/              # FastAPI（Phase 4）
│   ├── db/               # 数据库（Phase 2+）
│   └── config.py         # 配置管理
├── ui/                    # Streamlit UI（Phase 9）
├── tests/                 # 测试代码
├── scripts/               # 辅助脚本
├── ops/                   # Docker 等（Phase 10）
├── .env                   # 你的私有配置
├── requirements.txt       # 依赖清单
├── README.md              # 项目总览
└── PHASE1_GUIDE.md        # ? 从这里开始
```

---

## ? 下一步

? 打开 `PHASE1_GUIDE.md` 开始编码！

