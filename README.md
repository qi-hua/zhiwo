### 一.基本情况

#### 1.服务
目前有2个服务:

get_sparql_service:
无参考信息，直接大模型推理得到查询语句；

get_sparql_by_rag_service:
带入参考信息，通过rag推理得到查询语句；
****************************************

#### 2.agent
prompt位置分别在下面的2个文件中，结合模型情况修改：
app/core/agent/get_sparql_agent/get_sparql_agent.yaml

app/core/agent/get_sparql_agent/get_sparql_by_rag_agent.yaml

其中通过设置knowledge_similarity_top_k，控制传入的知识库数量
```
action:
  knowledge:
    - 'sparql_train_knowledge'
  knowledge_similarity_top_k:
    6
```
****************************************

#### 3.rag
rag使用的是ollama部署的shaw/dmeta-embedding-zh模型，需要提前下载；
或根据需要配置其他模型；

rag根据题目与知识库中的题目进行相似度计算，返回相似度top_k个题目与查询语句作为 背景信息；如果需要修改返回的格式修改app/core/knowledge/sparql_knowledge/sparql_knowledge.py第69行。
```python
doc.text = "问题：{}\tSPARQL查询语句：{}".format(doc.metadata.pop('question'),doc.metadata.pop('sparql'))
```
****************************************

#### 4.llm
大模型使用的是openAI风格的接口，需要设置环境变量，在以下文件进行修改：
config/custom_key.toml

### 二.需要修改的配置

config/custom_key.toml

可选：

app/core/llm/qwen2_llm.yaml

app/core/agent/get_sparql_agent/get_sparql_agent.yaml

app/core/agent/get_sparql_agent/get_sparql_by_rag_agent.yaml

app/core/knowledge/sparql_knowledge/sparql_knowledge.py

（端口默认8080，可进行配置修改）config/gunicorn_config.toml

### 三.运行

pip install -r requirements.txt

cd app/bootstrap
python server_application.py

注：修改配置文件后需要重启服务

### 四.测试

app/test/test.ipynb中有API调用的基本示例
```python
import json
import requests

def run_llm_service(question, service_id="get_sparql_service"):
    body = {
        "service_id": service_id,
        "params": {"input": question}
    }
    server_url = "http://127.0.0.1:8080/service_run"
    headers = { "Content-Type": "application/json" }
    response = requests.post(server_url, json=body, headers=headers)

    print(response.json())
```