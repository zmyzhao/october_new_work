# 知域：公共卫生 × 计算机科学

这是一个循序搭建中的本地原型。`index.html` 是现有网页；`data/` 放项目自行整理并核验的资料表；`backend/` 是 Python 后端框架，负责读取资料、检索并在配置后调用 AI API。

## 文件分别做什么

- `index.html`：网页本身。目前页面样式和演示交互仍写在这个文件里，显示的是内置示例结果。
- `data/concepts.csv`：公共卫生与计算机科学概念表。
- `data/methods.csv`：研究方法、所需条件和局限。
- `data/mappings.csv`：两门学科之间的概念映射关系。
- `data/sources.csv`：官方定义、论文或数据集的出处信息。
- `backend/main.py`：本地网页服务器和 `/api/query` 查询入口。
- `backend/retrieval.py`：读取 CSV，并做第一版关键词匹配。
- `backend/ai_service.py`：配置好服务地址、模型和 API 密钥后调用兼容 Chat Completions 的模型服务。
- `.env.example`：密钥配置示例。复制为 `.env` 后填写真实设置；不要分享或提交 `.env`。
- `requirements.txt`：运行 Python 后端所需依赖。

## 在 Windows 上启动

1. 用 VS Code 打开本项目总文件夹。
2. 安装 Python 3.11 或更新版本。首次配置时，在 VS Code 的“终端 → 新建终端”执行：

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

3. 在终端启动后端：

   ```powershell
   python -m uvicorn backend.main:app --reload
   ```

4. 浏览器打开 `http://127.0.0.1:8000/`。查看后端是否启动，可打开 `http://127.0.0.1:8000/api/health`。
5. 测试接口时可在 `http://127.0.0.1:8000/docs` 查看自动生成的接口页面。

如果 PowerShell 阻止虚拟环境激活，可在 VS Code 终端切换到 Command Prompt，再执行 `.venv\\Scripts\\activate.bat`。

## 先填资料，再配置 AI

CSV 文件可以用 Excel 打开。第一行是列名，后续每行填写一条资料。建议先少量填写，并为每条正式知识记录可核验的来源编号。`source_ids` 多个编号之间用英文分号 `;` 分隔。当前模板是空表，所以查询接口会提示知识库尚无资料。

当前 `retrieval.py` 使用简单关键词匹配，尚未实现 embedding 或向量数据库。准备好 AI 服务后，将 `.env.example` 复制为 `.env`，填入服务方提供的 Chat Completions URL、API key 和模型名称。不要把真实密钥写进网页文件或发到群聊、公开仓库。

## 当前还没有完成的连接

现有 `index.html` 仍显示前端内置的演示结果；Python `/api/query` 已单独搭好，但网页表单还没有改成调用它。下一步开发需要将表单提交连接到 `/api/query`，再把返回的回答和来源显示在页面中。AI 接口也只有在填写服务商配置并成功连通后才会真正调用模型。
