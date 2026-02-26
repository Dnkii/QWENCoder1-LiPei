"""
系统配置文件
定义各种参数和设置
"""

# 大模型相关配置
LLM_CONFIG = {
    'model_name': 'gpt-4',  # 使用的大模型名称
    'api_key': '',          # API密钥，实际使用时应从环境变量读取
    'temperature': 0.1      # 控制输出随机性
}

# 文档分类配置
CLASSIFICATION_CONFIG = {
    'supported_types': ['medical_record', 'accident_report', 'invoice', 'identity_card', 'bank_statement'],
    'confidence_threshold': 0.8
}

# 关键字提取配置
KEYWORD_EXTRACTION_CONFIG = {
    'max_keywords': 20,
    'extraction_method': 'llm_based'  # 可选: llm_based, rule_based, hybrid
}

# 责任评估配置
LIABILITY_EVALUATION_CONFIG = {
    'evaluation_method': 'rule_engine',  # 可选: rule_engine, ml_model, hybrid
    'confidence_threshold': 0.75
}

# 文件路径配置
PATH_CONFIG = {
    'upload_dir': '../data/upload/',
    'processed_dir': '../data/processed/',
    'model_cache_dir': '../data/models/'
}