# 智能植物养护系统

基于YOLOv8和知识图谱的植物识别与病虫害诊断平台。

## 功能特性

- 🌿 **植物识别**：基于 YOLOv8 的植物分类模型，支持120+种植物识别
- 🐛 **病害诊断**：自动检测植物病虫害，提供防治方案
- 📊 **知识图谱**：基于 Neo4j 的植物养护知识库，包含114种植物详细信息
- 💧 **养护管理**：浇水、施肥、修剪等养护记录追踪
- ⏰ **智能提醒**：自定义养护提醒，不再错过任何养护时机
- 🎯 **个性推荐**：根据用户偏好智能推荐适合的植物

## 快速启动

### 前置要求

1. Python 3.9+
2. MySQL 数据库
3. Neo4j 图数据库（可选，用于知识图谱功能）
4. Conda（推荐）

### 安装步骤

```bash
# 1. 激活环境
conda activate plant

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
# 编辑 backend/.env 文件，设置数据库密码和 Neo4j 配置

# 4. 构建知识图谱（可选但推荐）
cd knowledge_graph
python build_knowledge_graph.py
cd ..

# 5. 启动后端
cd backend
python app/main.py
```

### 知识图谱配置

如果你想要使用知识图谱功能：

1. **安装 Neo4j**：确保 Neo4j 服务正在运行
2. **配置连接**：编辑 `backend/.env` 文件
   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password  # 修改为你的密码
   NEO4J_DATABASE=neo4j
   ```
3. **导入数据**：
   ```bash
   cd knowledge_graph
   python build_knowledge_graph.py
   ```

详细使用说明请查看 [knowledge_graph/README.md](knowledge_graph/README.md)

## 项目结构

```
smart-plant-care/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/
│   │   │   ├── core/       # 核心配置和工具
│   │   │   ├── models/     # 数据模型
│   │   │   ├── schemas/    # Pydantic 模式
│   │   │   ├── services/   # 业务逻辑
│   │   │   └── v1/         # API 路由
│   │   └── utils/          # 工具函数
│   └── .env                # 环境配置
├── ai_models/              # AI 模型和训练脚本
│   ├── models/             # 训练好的模型
│   └── scripts/            # 数据处理和训练脚本
├── knowledge_graph/        # 知识图谱相关
│   ├── build_knowledge_graph.py  # 数据导入脚本
│   └── README.md           # 知识图谱使用指南
├── frontend/               # Vue3 前端
└── information             # 植物信息数据源
```

## API 文档

启动后端后，访问 http://localhost:8000/docs 查看完整的 API 文档。

## 技术栈

- **后端**：FastAPI, SQLAlchemy, Pydantic
- **AI 模型**：YOLOv8, PyTorch, OpenCV
- **知识图谱**：Neo4j, neo4j-driver
- **前端**：Vue 3, TypeScript, Element Plus, Vite
- **数据库**：MySQL, Redis（缓存）

## 开发指南

### 添加新植物数据

1. 在 `information` 文件中添加植物信息
2. 重新运行知识图谱构建脚本：
   ```bash
   cd knowledge_graph
   python build_knowledge_graph.py
   ```

### 训练自己的模型

参考 `ai_models/scripts/` 目录下的训练脚本：
- `train_plant_classifier.py` - 植物分类模型训练
- `train_disease_detector.py` - 病害检测模型训练

## 常见问题

### Q: Neo4j 连接失败？
A: 检查 `.env` 文件中的密码配置是否正确，确保 Neo4j 服务已启动。

### Q: 如何清空知识图谱重新导入？
A: 在 Neo4j Browser 中执行 `MATCH (n) DETACH DELETE n`，然后重新运行构建脚本。

### Q: 模型识别不准确？
A: 可以尝试用自己的数据重新训练模型，参考 `ai_models/scripts/` 中的训练脚本。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！