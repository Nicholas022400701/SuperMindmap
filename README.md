# 超级思维导图系统 (Super Mind Map System)

这项目是个牛逼的思维导图工具。你给它一个关键词，它就用 AI 帮你生成一个思维导图。

## 许可协议 (License)

本作品采用 <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">知识共享署名-非商业性使用-相同方式共享 4.0 国际许可协议</a> 进行许可。

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="知识共享许可协议" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a>

## 主要功能

*   **AI 生成导图 (ADD):** 你输入一个词，比如“人工智能”，后端就会去请求一个 AI 模型，然后返回一个树状的思维导图 JSON 数据。这个数据会被存到 MySQL 数据库里。
*   **智能节点合并 (COMBINE):** 这是个核心功能。如果你生成的几个思维导图里有内容很像的节点（比如“AI”和“人工智能”），系统会自动把它们合并成一个。它用的是高大上的“语义向量相似度”来判断，不是简单的文字比较。合并后，会保留先创建的那个节点的标题，然后把两个节点的孩子都收养过来。
*   **3D 可视化:** 前端用一个很酷的 3D 图来展示整个思维导图网络。你可以用鼠标在里面转、拉、缩放，跟飞一样。
*   点击任何节点，可以将其子树导出为 JSON 文件。
*   删除节点树

## 技术栈

*   **后端:** Python + FastAPI
*   **前端:** React
*   **数据库:** MySQL
*   **AI / 语义:** 通过 API 调用外部模型（比如 OpenAI 的）

## 如何运行

1.  **配置后端:**
    *   在 `backend` 文件夹里创建一个 `.env` 文件。
    *   在里面填上数据库地址和 AI 模型的 API Key 和地址。
    *   `DATABASE_URL="mysql+mysqlconnector://用户名:密码@地址:端口/数据库名"`
    *   `OPENAI_API_KEY="你的LLM的key"`
    *   `OPENAI_BASE_URL="你的LLM的地址"`
    *   `EMBEDDING_API_KEY="你的Embedding模型的KEY"`
    *   `API_BASE="你的Embedding模型的地址"`
2.  **运行后端:**
    *   先用Powershell或类似终端进到 `backend` 目录，
    *   安装依赖：`pip install -r requirements.txt`
    *   或者安装虚拟环境再装依赖（你喜欢咯）：`python -m venv venv` 然后 `.\venv\Scripts\activate` 最后 `pip install -r requirements.txt`
    *   然后运行：`uvicorn app.main:app --host 0.0.0.0 --port 8000`
3.  **运行前端:**
    *   先新开一个Powershell或类似终端窗口，激活刚刚的虚拟环境（如果你创建了的话）
    *   然后进到 `frontend` 目录，安装依赖：`npm install`
    *   然后运行：`npm start`
5.  **打开浏览器:** 访问 `http://localhost:3000` 就能看到界面了。

## 未来可能添加的功能
*   更好的可视化（将文字放在节点中）
