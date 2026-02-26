"""
关键字提取服务
从分类后的文档中提取预设的关键字段
"""
import re
from typing import List, Dict, Any
from datetime import datetime
import uuid

from ..models.claim import DocumentType, ExtractedField, ExtractionResult


class KeywordExtractor:
    """
    关键字提取器
    根据文档类型从文档中提取相应的关键字段
    """
    
    def __init__(self):
        """
        初始化关键字提取器
        定义不同文档类型对应的关键字段
        """
        # 定义每种文档类型需要提取的字段
        self.field_definitions = {
            DocumentType.MEDICAL_RECORD: [
                {"name": "patient_name", "pattern": r"患者[：:]\s*([^\n\r]+)", "description": "患者姓名"},
                {"name": "diagnosis", "pattern": r"(诊断|初步诊断)[：:]\s*([^\n\r]+)", "description": "诊断结果"},
                {"name": "admission_date", "pattern": r"(入院日期|住院日期)[：:]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日天]?)", "description": "入院日期"},
                {"name": "discharge_date", "pattern": r"(出院日期)[：:]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日天]?)", "description": "出院日期"},
                {"name": "hospital_name", "pattern": r"(医院|医疗机构)[：:]\s*([^\n\r]+)", "description": "医院名称"},
                {"name": "doctor_name", "pattern": r"(主治医师|医生)[：:]\s*([^\n\r]+)", "description": "医生姓名"}
            ],
            DocumentType.ACCIDENT_REPORT: [
                {"name": "accident_date", "pattern": r"(事故日期|发生时间)[：:]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日天]?)", "description": "事故日期"},
                {"name": "accident_location", "pattern": r"(事故地点|现场位置)[：:]\s*([^\n\r]+)", "description": "事故地点"},
                {"name": "parties_involved", "pattern": r"(当事人|涉事人员)[：:]\s*([^\n\r]+)", "description": "涉及人员"},
                {"name": "accident_description", "pattern": r"(事故经过|简要描述)[：:]\s*([^\n\r]+)", "description": "事故描述"},
                {"name": "police_station", "pattern": r"(交警队|派出所)[：:]\s*([^\n\r]+)", "description": "执法单位"}
            ],
            DocumentType.INVOICE: [
                {"name": "invoice_number", "pattern": r"(发票号码|发票号)[：:]\s*([A-Z\d]+)", "description": "发票号码"},
                {"name": "invoice_amount", "pattern": r"(金额|合计)[：:]\s*([¥￥\$\w]+\d+(?:\.\d+)?)", "description": "发票金额"},
                {"name": "invoice_date", "pattern": r"(开票日期|日期)[：:]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日天]?)", "description": "开票日期"},
                {"name": "provider", "pattern": r"(销售方|收款方|供应商)[：:]\s*([^\n\r]+)", "description": "提供商"},
                {"name": "recipient", "pattern": r"(购买方|付款方|客户)[：:]\s*([^\n\r]+)", "description": "接收方"}
            ],
            DocumentType.IDENTITY_CARD: [
                {"name": "name", "pattern": r"姓名[：:]\s*([^\n\r]+)", "description": "姓名"},
                {"name": "id_number", "pattern": r"身份证号[：:]\s*(\d{17}[\dXx])", "description": "身份证号"},
                {"name": "gender", "pattern": r"性别[：:]\s*([^\n\r]+)", "description": "性别"},
                {"name": "birth_date", "pattern": r"出生[：:]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日天]?)", "description": "出生日期"},
                {"name": "address", "pattern": r"住址[：:]\s*([^\n\r]+)", "description": "地址"}
            ],
            DocumentType.BANK_STATEMENT: [
                {"name": "account_number", "pattern": r"(账号|卡号)[：:]\s*([\d\s]+)", "description": "账户号码"},
                {"name": "account_holder", "pattern": r"(户名|账户持有人)[：:]\s*([^\n\r]+)", "description": "账户持有人"},
                {"name": "balance", "pattern": r"(余额|当前余额)[：:]\s*([¥￥\$\w]+\d+(?:\.\d+)?)", "description": "余额"},
                {"name": "statement_period", "pattern": r"(账单期间|对账单期间)[：:]\s*([^\n\r]+)", "description": "账单期间"}
            ],
            DocumentType.INSURANCE_CONTRACT: [
                {"name": "policy_number", "pattern": r"(保单号|保险单号)[：:]\s*([A-Z\d]+)", "description": "保单号"},
                {"name": "policy_holder", "pattern": r"(投保人)[：:]\s*([^\n\r]+)", "description": "投保人"},
                {"name": "insured_person", "pattern": r"(被保险人)[：:]\s*([^\n\r]+)", "description": "被保险人"},
                {"name": "coverage_amount", "pattern": r"(保险金额|保额)[：:]\s*([¥￥\$\w]+\d+(?:\.\d+)?)", "description": "保险金额"},
                {"name": "effective_date", "pattern": r"(生效日期|保险期间)[：:]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日天]?)", "description": "生效日期"}
            ]
        }
    
    async def extract_from_document(self, document_path: str, document_type: DocumentType) -> ExtractionResult:
        """
        从单个文档中提取关键字
        
        Args:
            document_path: 文档路径
            document_type: 文档类型
            
        Returns:
            提取结果
        """
        # 获取文档ID（从文件名或路径中提取）
        doc_id = str(uuid.uuid4())
        
        # 获取文档内容
        content = self._extract_text_from_document(document_path)
        
        # 根据文档类型提取字段
        extracted_fields = self._extract_fields_by_type(content, document_type)
        
        # 计算提取准确性（简化版）
        accuracy = self._calculate_extraction_accuracy(extracted_fields)
        
        return ExtractionResult(
            document_id=doc_id,
            extracted_fields=extracted_fields,
            extraction_accuracy=accuracy
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
            return f"模拟文档内容来自: {document_path}\n患者：张三\n诊断：急性阑尾炎\n入院日期：2023年10月5日\n出院日期：2023年10月10日\n医院：XX市人民医院\n主治医师：李医生\n发票号码：12345678\n发票金额：¥5000.00\n开票日期：2023年10月10日"
    
    def _extract_fields_by_type(self, content: str, doc_type: DocumentType) -> List[ExtractedField]:
        """
        根据文档类型提取相应字段
        
        Args:
            content: 文档内容
            doc_type: 文档类型
            
        Returns:
            提取的字段列表
        """
        if doc_type not in self.field_definitions:
            return []
        
        fields_to_extract = self.field_definitions[doc_type]
        extracted_fields = []
        
        for field_def in fields_to_extract:
            pattern = field_def["pattern"]
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            if matches:
                # 取第一个匹配项作为字段值
                field_value = matches[0] if isinstance(matches[0], str) else matches[0][-1]
                
                # 估算置信度（基于正则匹配的确定性）
                confidence = 0.9
                
                extracted_field = ExtractedField(
                    field_name=field_def["name"],
                    field_value=field_value.strip(),
                    confidence=confidence
                )
                
                extracted_fields.append(extracted_field)
        
        return extracted_fields
    
    def _calculate_extraction_accuracy(self, extracted_fields: List[ExtractedField]) -> float:
        """
        计算提取准确性
        
        Args:
            extracted_fields: 提取的字段列表
            
        Returns:
            准确性分数
        """
        if not extracted_fields:
            return 0.0
        
        # 简化的准确性计算：基于提取字段的数量和置信度
        total_confidence = sum(field.confidence for field in extracted_fields)
        avg_confidence = total_confidence / len(extracted_fields) if extracted_fields else 0.0
        
        # 假设理想情况下能提取10个字段，则根据实际提取数量调整分数
        ideal_field_count = 5  # 假设理想提取字段数
        field_ratio = min(len(extracted_fields) / ideal_field_count, 1.0)
        
        # 综合考虑字段完整性和置信度
        accuracy = (avg_confidence * 0.7 + field_ratio * 0.3)
        
        return accuracy
    
    async def extract_claim_information(self, claim_id: str):
        """
        提取整个理赔案件的信息
        
        Args:
            claim_id: 理赔ID
        """
        # 这里应该从数据库获取理赔文档及其分类结果
        # 为了演示，我们模拟一些数据
        documents_info = self._get_claim_documents_with_types(claim_id)
        
        extraction_results = []
        for doc_path, doc_type in documents_info:
            result = await self.extract_from_document(doc_path, doc_type)
            extraction_results.append(result)
        
        # 保存提取结果到数据库
        self._save_extraction_results(claim_id, extraction_results)
        
        return extraction_results
    
    def _get_claim_documents_with_types(self, claim_id: str) -> List[tuple]:
        """
        获取理赔案件的文档及类型信息
        这里是模拟实现
        
        Args:
            claim_id: 理赔ID
            
        Returns:
            (文档路径, 文档类型) 列表
        """
        # 在实际应用中，这里应该查询数据库获取文档路径和分类结果
        return [
            (f"/tmp/claims/{claim_id}/medical_record.pdf", DocumentType.MEDICAL_RECORD),
            (f"/tmp/claims/{claim_id}/invoice.pdf", DocumentType.INVOICE),
            (f"/tmp/claims/{claim_id}/contract.pdf", DocumentType.INSURANCE_CONTRACT)
        ]
    
    def _save_extraction_results(self, claim_id: str, results: List[ExtractionResult]):
        """
        保存提取结果到数据库
        这里是占位实现
        
        Args:
            claim_id: 理赔ID
            results: 提取结果列表
        """
        # 在实际应用中，这里应该将结果保存到数据库
        print(f"保存理赔 {claim_id} 的提取结果: {len(results)} 个文档已处理")