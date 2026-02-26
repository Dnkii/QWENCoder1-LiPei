"""
理赔模型定义
定义理赔相关的数据模型
"""
from enum import Enum
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class ClaimStatus(str, Enum):
    """理赔状态枚举"""
    UPLOADED = "uploaded"          # 已上传
    CLASSIFYING = "classifying"     # 正在分类
    EXTRACTING = "extracting"      # 正在提取信息
    EVALUATING = "evaluating"      # 正在评估责任
    COMPLETED = "completed"        # 完成
    REJECTED = "rejected"          # 拒绝


class DocumentType(str, Enum):
    """文档类型枚举"""
    MEDICAL_RECORD = "medical_record"      # 病历
    ACCIDENT_REPORT = "accident_report"    # 事故报告
    INVOICE = "invoice"                   # 发票
    IDENTITY_CARD = "identity_card"        # 身份证
    BANK_STATEMENT = "bank_statement"      # 银行流水
    INSURANCE_CONTRACT = "insurance_contract"  # 保险合同


class ClaimDocument(BaseModel):
    """理赔文档模型"""
    id: str
    filename: str
    document_type: DocumentType
    file_path: str
    upload_time: datetime
    classification_confidence: float


class ExtractedField(BaseModel):
    """提取字段模型"""
    field_name: str
    field_value: str
    confidence: float
    page_number: Optional[int] = None
    position: Optional[Dict] = None  # 字段在文档中的位置


class ClassificationResult(BaseModel):
    """分类结果模型"""
    document_id: str
    predicted_type: DocumentType
    confidence: float
    alternative_types: Optional[List[DocumentType]] = None


class ExtractionResult(BaseModel):
    """提取结果模型"""
    document_id: str
    extracted_fields: List[ExtractedField]
    extraction_accuracy: float


class LiabilityEvaluation(BaseModel):
    """责任评估模型"""
    coverage_applicable: bool  # 是否在保障范围内
    exclusion_factors: List[str]  # 免责因素
    coverage_limit: Optional[float] = None  # 保障限额
    recommended_payout: float  # 建议赔付金额
    evaluation_reasons: List[str]  # 评估理由
    confidence: float


class ClaimModel(BaseModel):
    """理赔主模型"""
    id: str
    status: ClaimStatus
    documents: List[str]  # 文档路径列表
    policy_holder: Optional[str] = None  # 投保人
    insured_person: Optional[str] = None  # 被保险人
    incident_date: Optional[datetime] = None  # 出险日期
    claim_amount: Optional[float] = None  # 索赔金额
    classification_results: Optional[List[ClassificationResult]] = None
    extraction_results: Optional[List[ExtractionResult]] = None
    liability_evaluation: Optional[LiabilityEvaluation] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()