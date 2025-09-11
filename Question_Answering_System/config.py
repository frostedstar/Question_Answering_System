LLM_CONFIG = {
    'API_KEY':"sk-b73a7f714f8c4af789d3bc5abe00241e",
    "API_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1" ,
    # "Model": "deepseek-r1"，
    "Model": "qwen-plus",
    # "Model":"qwen-turbo"
}

EMBEDDING_CONFIG = {
    'local': {
        'base_url': "http://localhost:1234/v1",
        'model': "BAAI/BAAI_bge-large-zh-v1.5/bge-large-zh-v1.5-f32.gguf"
    }
}