import streamlit as st
import sqlite3
import requests
import fitz  # PyMuPDF，用于处理PDF文件
from docx import Document  # 用于处理Word文档

# ---------- 数据库管理 ----------
def init_db():
    # 初始化数据库，创建存储API配置的表
    conn = sqlite3.connect("api_data.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT,
            deployment_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_credentials():
    # 获取最新一条API配置
    conn = sqlite3.connect("api_data.db")
    c = conn.cursor()
    c.execute("SELECT api_key, deployment_url FROM credentials ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row

def save_credentials(api_key, deployment_url):
    # 保存用户输入的API Key和部署URL
    conn = sqlite3.connect("api_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO credentials (api_key, deployment_url) VALUES (?, ?)", (api_key, deployment_url))
    conn.commit()
    conn.close()

# ---------- IBM Token 获取 ----------
def get_ibm_token(api_key):
    # 使用API Key从IBM Cloud获取访问令牌
    token_url = 'https://iam.cloud.ibm.com/identity/token'
    data = {
        "apikey": api_key,
        "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        st.error("❌ Failed to retrieve token. Please check your API Key.")
        return None

# ---------- 模型推理 ----------
def perform_inference(messages, token, deployment_url):
    # 发送带上下文的消息给模型服务进行推理
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {
        "messages": messages
    }
    response = requests.post(deployment_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"❌ Model call failed: {response.status_code} - {response.text}")
        return None

# ---------- 文件文本提取 ----------
def extract_text_from_pdf(pdf_file):
    # 从PDF文件中提取文字
    text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(docx_file):
    # 从Word文档中提取文字
    doc = Document(docx_file)
    return "\n".join(p.text for p in doc.paragraphs)

# ---------- UI 初始化 ----------
st.set_page_config(page_title="Watsonx Human Ethics Assistant", layout="centered")
st.title("📋 Human Ethics Checker - IBM Watsonx")

init_db()  # 初始化数据库
credentials = get_credentials()
default_api_key = credentials[0] if credentials else ""
default_deployment_url = credentials[1] if credentials else ""

# 初始化聊天历史session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- API 配置区块 ----------
with st.expander("🔐 Configure API Key and Deployment URL"):
    api_key = st.text_input("API Key", value=default_api_key, type="password")
    deployment_url = st.text_input("Model Deployment URL", value=default_deployment_url)
    if st.button("💾 Save Configuration"):
        save_credentials(api_key, deployment_url)
        st.success("✅ Configuration Saved!")

# ---------- 聊天输入 ----------
st.subheader("💬 Ask About Human Ethics")
user_query = st.chat_input("Ask something like: 'Does this application meet NEAC guidelines?'")

if user_query:
    # 将用户输入添加到对话历史中
    st.session_state.chat_history.append({"role": "user", "content": user_query})

    # 获取令牌并执行推理
    token = get_ibm_token(api_key)
    if token:
        response = perform_inference(st.session_state.chat_history, token, deployment_url)
        if response:
            reply = response["choices"][0]["message"]["content"]
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

# ---------- 显示聊天记录 ----------
for msg in st.session_state.chat_history:
    speaker = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
    st.markdown(f"**{speaker}:** {msg['content']}")

# ---------- 上传文档 ----------
st.subheader("📎 Upload Research Application for Review")
uploaded_file = st.file_uploader("Upload PDF or Word Document", type=["pdf", "docx"])

if uploaded_file:
    # 根据文件类型提取内容
    if uploaded_file.name.endswith(".pdf"):
        file_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        file_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Only PDF and DOCX are supported.")
        file_text = None

    if file_text:
        # 成功加载文件后显示部分内容
        st.success("✅ File loaded successfully!")
        st.text_area("📄 File Preview", file_text[:1500] + "...", height=300)

        if st.button("🔍 Analyze This Document"):
            # 对文档前3000字进行分析
            token = get_ibm_token(api_key)
            if token:
                prompt = f"As an ethics reviewer, please assess whether the following research application complies with NEAC and UAHPEC guidelines:\n\n{file_text[:3000]}"
                st.session_state.chat_history.append({"role": "user", "content": prompt})

                response = perform_inference(st.session_state.chat_history, token, deployment_url)
                if response:
                    reply = response["choices"][0]["message"]["content"]
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
