"""
理赔相关API端点
"""
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from typing import Optional
import uuid

from ..models.claim import ClaimModel, ClaimStatus
from ..services.document_classifier import DocumentClassifier
from ..services.keyword_extractor import KeywordExtractor
from ..services.liability_evaluator import LiabilityEvaluator

router = APIRouter(prefix="/api")

# 初始化服务
classifier = DocumentClassifier()
extractor = KeywordExtractor()
evaluator = LiabilityEvaluator()

# 存储理赔数据（在实际应用中，应使用数据库）
claims_storage = {}

@router.post("/upload")
async def upload_claim_documents(files: list[UploadFile] = File(...)):
    """
    上传理赔文档
    """
    claim_id = str(uuid.uuid4())
    
    # 保存上传的文件（在实际应用中，应保存到适当的存储位置）
    file_paths = []
    for file in files:
        # 在实际实现中，这里应该将文件保存到磁盘或云存储
        file_path = f"uploads/{claim_id}/{file.filename}"
        file_paths.append(file_path)
    
    # 创建理赔记录
    claim = ClaimModel(
        id=claim_id,
        status=ClaimStatus.UPLOADED,
        documents=file_paths
    )
    
    # 临时存储理赔信息
    claims_storage[claim_id] = claim.dict()
    
    return {
        "claim_id": claim_id,
        "message": "文档上传成功",
        "document_count": len(files)
    }

@router.get("/claims/{claim_id}")
async def get_claim(claim_id: str):
    """
    获取理赔详情
    """
    if claim_id not in claims_storage:
        raise HTTPException(status_code=404, detail="理赔记录不存在")
    
    claim_data = claims_storage[claim_id]
    return claim_data

@router.post("/classify/{claim_id}")
async def classify_documents(claim_id: str, background_tasks: BackgroundTasks):
    """
    对理赔文档进行分类
    """
    if claim_id not in claims_storage:
        raise HTTPException(status_code=404, detail="理赔记录不存在")
    
    # 更新理赔状态
    claim_data = claims_storage[claim_id]
    claim_data["status"] = ClaimStatus.CLASSIFYING
    claims_storage[claim_id] = claim_data
    
    # 添加后台任务进行分类
    background_tasks.add_task(_perform_classification, claim_id)
    
    return {
        "claim_id": claim_id,
        "message": "文档分类任务已启动"
    }

@router.post("/extract/{claim_id}")
async def extract_information(claim_id: str, background_tasks: BackgroundTasks):
    """
    从理赔文档中提取信息
    """
    if claim_id not in claims_storage:
        raise HTTPException(status_code=404, detail="理赔记录不存在")
    
    # 更新理赔状态
    claim_data = claims_storage[claim_id]
    claim_data["status"] = ClaimStatus.EXTRACTING
    claims_storage[claim_id] = claim_data
    
    # 添加后台任务进行信息提取
    background_tasks.add_task(_perform_extraction, claim_id)
    
    return {
        "claim_id": claim_id,
        "message": "信息提取任务已启动"
    }

@router.post("/evaluate/{claim_id}")
async def evaluate_liability(claim_id: str, contract_terms: Optional[str] = None):
    """
    评估理赔责任
    """
    if claim_id not in claims_storage:
        raise HTTPException(status_code=404, detail="理赔记录不存在")
    
    # 更新理赔状态
    claim_data = claims_storage[claim_id]
    claim_data["status"] = ClaimStatus.EVALUATING
    claims_storage[claim_id] = claim_data
    
    # 执行责任评估
    liability_result = evaluator.evaluate_claim(claim_id, contract_terms)
    
    # 更新理赔数据
    claim_data["liability_evaluation"] = liability_result.dict()
    claim_data["status"] = ClaimStatus.COMPLETED
    claims_storage[claim_id] = claim_data
    
    return {
        "claim_id": claim_id,
        "liability_result": liability_result
    }

@router.get("/reports/{claim_id}")
async def generate_report(claim_id: str):
    """
    生成理赔报告
    """
    if claim_id not in claims_storage:
        raise HTTPException(status_code=404, detail="理赔记录不存在")
    
    claim_data = claims_storage[claim_id]
    
    # 构建报告
    report = {
        "claim_id": claim_id,
        "summary": f"理赔案件 {claim_id} 处理报告",
        "details": {
            "status": claim_data.get("status"),
            "document_count": len(claim_data.get("documents", [])),
            "classification_results": claim_data.get("classification_results"),
            "extraction_results": claim_data.get("extraction_results"),
            "liability_evaluation": claim_data.get("liability_evaluation")
        },
        "recommendation": "根据AI评估结果，建议按责任范围进行赔付"
    }
    
    return report

# 后台任务函数
async def _perform_classification(claim_id: str):
    """
    执行文档分类的后台任务
    """
    try:
        # 这里调用实际的分类服务
        classification_results = await classifier.classify_claim_documents(claim_id)
        
        # 更新理赔数据
        claim_data = claims_storage[claim_id]
        claim_data["classification_results"] = [result.dict() for result in classification_results]
        claim_data["status"] = ClaimStatus.EXTRACTING  # 分类完成后进入提取阶段
        claims_storage[claim_id] = claim_data
        
    except Exception as e:
        # 更新理赔数据为失败状态
        claim_data = claims_storage[claim_id]
        claim_data["status"] = ClaimStatus.REJECTED
        claims_storage[claim_id] = claim_data
        print(f"分类任务失败: {str(e)}")

async def _perform_extraction(claim_id: str):
    """
    执行信息提取的后台任务
    """
    try:
        # 这里调用实际的信息提取服务
        extraction_results = await extractor.extract_claim_information(claim_id)
        
        # 更新理赔数据
        claim_data = claims_storage[claim_id]
        claim_data["extraction_results"] = [result.dict() for result in extraction_results]
        claim_data["status"] = ClaimStatus.EVALUATING  # 提取完成后进入评估阶段
        claims_storage[claim_id] = claim_data
        
    except Exception as e:
        # 更新理赔数据为失败状态
        claim_data = claims_storage[claim_id]
        claim_data["status"] = ClaimStatus.REJECTED
        claims_storage[claim_id] = claim_data
        print(f"提取任务失败: {str(e)}")