"""
保险理赔助手主程序
整合文档分类、关键字提取和责任评估功能
"""
from .document_classifier import DocumentClassifier
from .keyword_extractor import KeywordExtractor
from .liability_evaluator import LiabilityEvaluator


class InsuranceClaimAssistant:
    def __init__(self):
        """
        初始化理赔助手
        """
        self.document_classifier = DocumentClassifier()
        self.keyword_extractor = KeywordExtractor()
        self.liability_evaluator = LiabilityEvaluator()
    
    def process_claim(self, document_path, contract_terms):
        """
        处理理赔案件
        
        Args:
            document_path: 理赔文档路径
            contract_terms: 保险合同条款
            
        Returns:
            dict: 理赔处理结果
        """
        # 1. 文档分类
        category = self.document_classifier.classify_document(document_path)
        
        # 2. 关键字提取
        keywords = self.keyword_extractor.extract_keywords(document_path, category)
        
        # 3. 责任评估
        liability_result = self.liability_evaluator.evaluate_liability(keywords, contract_terms)
        
        return {
            'category': category,
            'keywords': keywords,
            'liability_result': liability_result
        }


def main():
    """
    主函数，演示理赔助手的使用
    """
    assistant = InsuranceClaimAssistant()
    
    # 示例用法
    # document_path = "path/to/claim_document.pdf"
    # contract_terms = "保险合同条款内容"
    # result = assistant.process_claim(document_path, contract_terms)
    # print(result)


if __name__ == "__main__":
    main()