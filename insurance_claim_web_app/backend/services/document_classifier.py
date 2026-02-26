"""
文档分类服务
使用AI模型对上传的文档进行智能分类
"""
import os
from typing import List, Dict, Any
from pathlib import Path
import uuid

from ..models.claim import DocumentType, ClassificationResult


class DocumentClassifier:
    """
    文档分类器
    负责将上传的文档按照预设类型进行分类
    """
    
    def __init__(self):
        """
        初始化文档分类器
        可以在此加载预训练模型或其他资源
        """
        # 支持的文档类型列表
        self.supported_types = [
            DocumentType.MEDICAL_RECORD,
            DocumentType.ACCIDENT_REPORT,
            DocumentType.INVOICE,
            DocumentType.IDENTITY_CARD,
            DocumentType.BANK_STATEMENT,
            DocumentType.INSURANCE_CONTRACT
        ]
        
        # 模拟预设的分类关键词库
        self.keyword_mapping = {
            DocumentType.MEDICAL_RECORD: ["病历", "诊断", "入院", "出院", "医嘱", "检查", "检验", "病理", "门诊"],
            DocumentType.ACCIDENT_REPORT: ["事故", "现场", "交警", "认定书", "碰撞", "损伤", "报案", "调查"],
            DocumentType.INVOICE: ["发票", "金额", "费用", "收据", "结算", "收费", "凭证"],
            DocumentType.IDENTITY_CARD: ["身份证", "姓名", "性别", "出生", "地址", "证件"],
            DocumentType.BANK_STATEMENT: ["银行", "流水", "转账", "账户", "存款", "取款", "余额"],
            DocumentType.INSURANCE_CONTRACT: ["保险", "合同", "条款", "投保", "受益", "保费", "保障"]
        }
    
    async def classify_document(self, document_path: str) -> ClassificationResult:
        """
        对单个文档进行分类
        
        Args:
            document_path: 文档路径
            
        Returns:
            分类结果
        """
        # 获取文档ID（从文件名或路径中提取）
        doc_id = str(uuid.uuid4())
        
        # 获取文档内容（这里简化为读取文本，实际可能需要OCR或PDF解析）
        content = self._extract_text_from_document(document_path)
        
        # 执行分类逻辑
        predicted_type, confidence = self._classify_content(content)
        
        # 生成备选类型（模拟）
        alternative_types = self._get_alternative_types(predicted_type)
        
        return ClassificationResult(
            document_id=doc_id,
            predicted_type=predicted_type,
            confidence=confidence,
            alternative_types=alternative_types
        )
    
    def _extract_text_from_document(self, document_path: str) -> str:
        """
        从文档中提取文本内容
        这里简化处理，实际应用中可能需要使用OCR、PDF解析等技术
        
        Args:
            document_path: 文档路径
            
        Returns:
            提取的文本内容
        """
        # 如果是文本文件，直接读取
        if document_path.endswith('.txt'):
            with open(document_path, 'r', encoding='utf-8') as f:
                return f.read()
        # 如果是其他格式，返回模拟内容
        else:
            # 在实际实现中，这里需要根据文件类型使用相应的解析方法
            # 如使用PyPDF2解析PDF，使用PIL+pytesseract进行OCR等
            return f"模拟文档内容来自: {os.path.basename(document_path)}"
    
    def _classify_content(self, content: str) -> tuple[DocumentType, float]:
        """
        根据内容对文档进行分类
        
        Args:
            content: 文档内容
            
        Returns:
            (预测类型, 置信度)
        """
        # 计算每个类型的匹配分数
        scores = {}
        content_lower = content.lower()
        
        for doc_type, keywords in self.keyword_mapping.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    score += 1
            scores[doc_type] = score
        
        # 找到最高分的类型
        predicted_type = max(scores, key=scores.get)
        max_score = scores[predicted_type]
        
        # 计算置信度（简化版，实际可以更复杂的算法）
        total_keywords = sum(len(keywords) for keywords in self.keyword_mapping.values())
        confidence = min(max_score / max(1, total_keywords // len(self.keyword_mapping)), 1.0)
        
        # 如果没有找到任何关键词，返回默认类型
        if max_score == 0:
            return DocumentType.MEDICAL_RECORD, 0.1
        
        return predicted_type, confidence
    
    def _get_alternative_types(self, primary_type: DocumentType) -> List[DocumentType]:
        """
        获取备选类型列表
        
        Args:
            primary_type: 主要类型
            
        Returns:
            备选类型列表
        """
        # 返回除了主要类型之外的其他类型
        alternatives = [t for t in self.supported_types if t != primary_type]
        # 只返回前3个备选类型
        return alternatives[:3]
    
    async def classify_claim_documents(self, claim_id: str):
        """
        对整个理赔案件的所有文档进行分类
        
        Args:
            claim_id: 理赔ID
        """
        # 这里应该从数据库或存储中获取理赔相关文档
        # 为了演示，我们模拟一些文档路径
        document_paths = self._get_claim_documents(claim_id)
        
        classification_results = []
        for doc_path in document_paths:
            result = await self.classify_document(doc_path)
            classification_results.append(result)
        
        # 保存分类结果到数据库
        self._save_classification_results(claim_id, classification_results)
        
        return classification_results
    
    def _get_claim_documents(self, claim_id: str) -> List[str]:
        """
        获取理赔案件的文档列表
        这里是模拟实现
        
        Args:
            claim_id: 理赔ID
            
        Returns:
            文档路径列表
        """
        # 在实际应用中，这里应该查询数据库或文档存储系统
        # 返回与理赔ID关联的文档路径列表
        return [f"/tmp/claims/{claim_id}/doc_{i}.pdf" for i in range(1, 4)]
    
    def _save_classification_results(self, claim_id: str, results: List[ClassificationResult]):
        """
        保存分类结果到数据库
        这里是占位实现
        
        Args:
            claim_id: 理赔ID
            results: 分类结果列表
        """
        # 在实际应用中，这里应该将结果保存到数据库
        print(f"保存理赔 {claim_id} 的分类结果: {len(results)} 个文档已分类")