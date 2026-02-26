"""
责任评估服务
根据提取的信息和保险合同条款评估理赔责任
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ..models.claim import (
    LiabilityEvaluation, 
    DocumentType, 
    ExtractedField, 
    ExtractionResult,
    ClassificationResult
)


class LiabilityEvaluator:
    """
    责任评估器
    根据提取的信息和保险合同条款评估理赔责任
    """
    
    def __init__(self):
        """
        初始化责任评估器
        加载保险产品条款和规则
        """
        # 模拟保险产品条款库
        self.policy_terms_db = {
            "health_insurance_basic": {
                "name": "基本医疗保险",
                "coverage": ["住院费用", "手术费用", "药品费用(医保目录内)"],
                "exclusions": ["既往症", "美容手术", "牙科治疗", "生育相关"],
                "limits": {
                    "年度报销上限": 100000,
                    "单次住院上限": 30000,
                    "自付比例": 0.1
                },
                "waiting_period": 30  # 等待期30天
            },
            "accident_insurance": {
                "name": "意外伤害保险",
                "coverage": ["意外身故", "意外伤残", "意外医疗费用"],
                "exclusions": ["自杀", "酒驾", "战争", "高风险运动"],
                "limits": {
                    "意外身故": 500000,
                    "意外医疗": 50000,
                    "伤残给付比例": "按伤残等级"
                },
                "waiting_period": 0
            }
        }
        
        # 风险规则库
        self.risk_rules = [
            {
                "name": "性别年龄不符",
                "condition": lambda fields: self._check_gender_age_inconsistency(fields),
                "severity": "high",
                "description": "被保险人性别与年龄不匹配"
            },
            {
                "name": "既往症检测",
                "condition": lambda fields: self._check_pre_existing_conditions(fields),
                "severity": "high",
                "description": "疑似既往症"
            },
            {
                "name": "费用异常高",
                "condition": lambda fields: self._check_abnormal_cost(fields),
                "severity": "medium",
                "description": "费用超出合理范围"
            },
            {
                "name": "诊断与用药不符",
                "condition": lambda fields: self._check_medication_diagnosis_match(fields),
                "severity": "high",
                "description": "药物与诊断不匹配"
            }
        ]
    
    def evaluate_claim(self, claim_id: str, contract_terms: Optional[str] = None) -> LiabilityEvaluation:
        """
        评估理赔责任
        
        Args:
            claim_id: 理赔ID
            contract_terms: 合同条款（可选，如果不提供则使用默认条款）
            
        Returns:
            责任评估结果
        """
        # 获取理赔的提取结果和分类结果
        extraction_results, classification_results = self._get_claim_data(claim_id)
        
        # 合并所有提取的字段
        all_extracted_fields = self._merge_extraction_results(extraction_results)
        
        # 解析合同条款
        policy_info = self._parse_policy_terms(contract_terms)
        
        # 检查保障范围
        coverage_applicable, coverage_issues = self._check_coverage(
            all_extracted_fields, 
            policy_info
        )
        
        # 检查免责条款
        exclusion_factors = self._check_exclusions(
            all_extracted_fields, 
            policy_info
        )
        
        # 应用风险规则
        risk_factors = self._apply_risk_rules(all_extracted_fields)
        
        # 计算建议赔付金额
        recommended_payout = self._calculate_recommended_payout(
            all_extracted_fields, 
            policy_info, 
            coverage_applicable, 
            exclusion_factors
        )
        
        # 计算整体置信度
        confidence = self._calculate_evaluation_confidence(
            coverage_applicable,
            len(exclusion_factors),
            len(risk_factors)
        )
        
        # 生成评估理由
        evaluation_reasons = self._generate_evaluation_reasons(
            coverage_applicable,
            coverage_issues,
            exclusion_factors,
            risk_factors
        )
        
        return LiabilityEvaluation(
            coverage_applicable=coverage_applicable,
            exclusion_factors=exclusion_factors,
            coverage_limit=policy_info.get("limits", {}).get("年度报销上限"),
            recommended_payout=recommended_payout,
            evaluation_reasons=evaluation_reasons,
            confidence=confidence
        )
    
    def _get_claim_data(self, claim_id: str) -> tuple[List[ExtractionResult], List[ClassificationResult]]:
        """
        获取理赔数据（提取结果和分类结果）
        这里是模拟实现
        
        Args:
            claim_id: 理赔ID
            
        Returns:
            (提取结果列表, 分类结果列表)
        """
        # 在实际应用中，这里应该从数据库查询理赔相关的数据
        return [], []
    
    def _merge_extraction_results(self, extraction_results: List[ExtractionResult]) -> Dict[str, Any]:
        """
        合并多个文档的提取结果
        
        Args:
            extraction_results: 提取结果列表
            
        Returns:
            合并后的字段字典
        """
        merged_fields = {}
        for result in extraction_results:
            for field in result.extracted_fields:
                merged_fields[field.field_name] = {
                    'value': field.field_value,
                    'confidence': field.confidence
                }
        return merged_fields
    
    def _parse_policy_terms(self, contract_terms: Optional[str]) -> Dict[str, Any]:
        """
        解析合同条款
        如果没有提供具体条款，则使用默认条款
        
        Args:
            contract_terms: 合同条款字符串
            
        Returns:
            解析后的条款信息
        """
        if contract_terms:
            # 在实际应用中，这里应该解析提供的合同条款
            # 为了演示，我们返回一个默认的基本医疗保险条款
            return self.policy_terms_db["health_insurance_basic"]
        else:
            # 默认使用基本医疗保险条款
            return self.policy_terms_db["health_insurance_basic"]
    
    def _check_coverage(self, fields: Dict[str, Any], policy_info: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        检查是否在保障范围内
        
        Args:
            fields: 提取的字段
            policy_info: 保险条款信息
            
        Returns:
            (是否在保障范围内, 保障问题列表)
        """
        issues = []
        
        # 检查等待期
        if "incident_date" in fields and policy_info.get("waiting_period", 0) > 0:
            # 这里需要实际计算日期差，简化处理
            pass
        
        # 检查保障范围
        diagnosis = fields.get("diagnosis", {}).get("value", "")
        if diagnosis:
            # 检查是否属于保障范围内的疾病
            coverage_items = policy_info.get("coverage", [])
            # 简化处理，假设大部分常见疾病都在保障范围内
            is_covered = True
        else:
            is_covered = False
            issues.append("缺少诊断信息，无法确认是否在保障范围内")
        
        return is_covered, issues
    
    def _check_exclusions(self, fields: Dict[str, Any], policy_info: Dict[str, Any]) -> List[str]:
        """
        检查免责情况
        
        Args:
            fields: 提取的字段
            policy_info: 保险条款信息
            
        Returns:
            免责因素列表
        """
        exclusions = policy_info.get("exclusions", [])
        exclusion_factors = []
        
        # 检查提取的字段是否涉及免责情况
        diagnosis = fields.get("diagnosis", {}).get("value", "").lower()
        treatment = fields.get("treatment_details", {}).get("value", "").lower()
        
        for exclusion in exclusions:
            if exclusion.lower() in diagnosis or exclusion.lower() in treatment:
                exclusion_factors.append(exclusion)
        
        return exclusion_factors
    
    def _apply_risk_rules(self, fields: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        应用风险规则
        
        Args:
            fields: 提取的字段
            
        Returns:
            风险因素列表
        """
        risk_factors = []
        
        for rule in self.risk_rules:
            if rule["condition"](fields):
                risk_factors.append({
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "description": rule["description"]
                })
        
        return risk_factors
    
    def _calculate_recommended_payout(self, 
                                    fields: Dict[str, Any], 
                                    policy_info: Dict[str, Any],
                                    coverage_applicable: bool,
                                    exclusion_factors: List[str]) -> float:
        """
        计算建议赔付金额
        
        Args:
            fields: 提取的字段
            policy_info: 保险条款信息
            coverage_applicable: 是否在保障范围内
            exclusion_factors: 免责因素列表
            
        Returns:
            建议赔付金额
        """
        if not coverage_applicable or exclusion_factors:
            return 0.0
        
        # 获取发票金额
        invoice_amount_str = fields.get("invoice_amount", {}).get("value", "0")
        # 提取数字部分
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', invoice_amount_str.replace(',', ''))
        if numbers:
            invoice_amount = float(numbers[0])
        else:
            invoice_amount = 0.0
        
        # 应用保险条款限制
        limits = policy_info.get("limits", {})
        max_coverage = limits.get("年度报销上限", float('inf'))
        self_pay_ratio = limits.get("自付比例", 0)
        
        # 计算实际赔付金额
        payout = invoice_amount * (1 - self_pay_ratio)
        
        # 不超过保障上限
        payout = min(payout, max_coverage)
        
        return round(payout, 2)
    
    def _calculate_evaluation_confidence(self, 
                                       coverage_applicable: bool,
                                       exclusion_count: int,
                                       risk_count: int) -> float:
        """
        计算评估置信度
        
        Args:
            coverage_applicable: 是否在保障范围内
            exclusion_count: 免责因素数量
            risk_count: 风险因素数量
            
        Returns:
            置信度分数
        """
        base_confidence = 0.9
        
        # 如果不在保障范围内或有免责因素，降低置信度
        if not coverage_applicable:
            base_confidence -= 0.3
        if exclusion_count > 0:
            base_confidence -= 0.2 * exclusion_count
        
        # 根据风险因素数量调整置信度
        if risk_count > 0:
            base_confidence -= 0.1 * risk_count
        
        return max(base_confidence, 0.1)  # 最低置信度为0.1
    
    def _generate_evaluation_reasons(self,
                                   coverage_applicable: bool,
                                   coverage_issues: List[str],
                                   exclusion_factors: List[str],
                                   risk_factors: List[Dict[str, Any]]) -> List[str]:
        """
        生成评估理由
        
        Args:
            coverage_applicable: 是否在保障范围内
            coverage_issues: 保障问题列表
            exclusion_factors: 免责因素列表
            risk_factors: 风险因素列表
            
        Returns:
            评估理由列表
        """
        reasons = []
        
        if coverage_applicable:
            reasons.append("案件在保险保障范围内")
        else:
            reasons.append("案件可能不在保障范围内")
            reasons.extend(coverage_issues)
        
        if exclusion_factors:
            reasons.append(f"发现{len(exclusion_factors)}个免责因素: {', '.join(exclusion_factors)}")
        
        if risk_factors:
            risk_names = [rf["name"] for rf in risk_factors]
            reasons.append(f"检测到{len(risk_factors)}个风险点: {', '.join(risk_names)}")
        
        if not coverage_issues and not exclusion_factors and not risk_factors:
            reasons.append("未发现明显风险或免责情况")
        
        return reasons
    
    # 风险规则的具体实现
    def _check_gender_age_inconsistency(self, fields: Dict[str, Any]) -> bool:
        """
        检查性别年龄不一致
        """
        gender = fields.get("gender", {}).get("value", "").lower()
        age_str = fields.get("age", {}).get("value", "")
        
        if not age_str.isdigit():
            # 尝试从出生日期计算年龄
            birth_date = fields.get("birth_date", {}).get("value", "")
            if birth_date:
                try:
                    from datetime import datetime
                    birth_dt = datetime.strptime(birth_date.replace("年", "-").replace("月", "-").replace("日", ""), "%Y-%m-%d")
                    age = (datetime.now() - birth_dt).days // 365
                except:
                    return False
            else:
                return False
        else:
            age = int(age_str)
        
        # 简单规则：如果性别是女性但年龄小于18岁怀孕相关，可能有问题
        if "女" in gender and age < 18:
            diagnosis = fields.get("diagnosis", {}).get("value", "").lower()
            if any(keyword in diagnosis for keyword in ["孕", "产", "妇科"]):
                return True
        
        return False
    
    def _check_pre_existing_conditions(self, fields: Dict[str, Any]) -> bool:
        """
        检查既往症
        """
        medical_history = fields.get("medical_history", {}).get("value", "").lower()
        diagnosis = fields.get("diagnosis", {}).get("value", "").lower()
        
        # 如果病史中包含当前诊断，则可能是既往症
        if medical_history and diagnosis:
            return diagnosis in medical_history
        
        return False
    
    def _check_abnormal_cost(self, fields: Dict[str, Any]) -> bool:
        """
        检查费用异常高
        """
        invoice_amount_str = fields.get("invoice_amount", {}).get("value", "0")
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', invoice_amount_str.replace(',', ''))
        
        if numbers:
            amount = float(numbers[0])
            # 简单规则：如果费用超过2万元，认为可能异常
            return amount > 20000
        
        return False
    
    def _check_medication_diagnosis_match(self, fields: Dict[str, Any]) -> bool:
        """
        检查药物与诊断是否匹配
        """
        diagnosis = fields.get("diagnosis", {}).get("value", "").lower()
        medications = fields.get("medications", {}).get("value", "").lower()
        
        # 简单规则：检查特定药物是否与诊断匹配
        if "抗生素" in medications and "感染" not in diagnosis and "炎症" not in diagnosis:
            return True  # 使用抗生素但没有感染或炎症诊断
        
        return False