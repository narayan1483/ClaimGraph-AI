"""
ClaimGraph AI — Evaluation API Router.

Endpoints for AI system benchmarks (RAG faithfulness, agent performance)
and ML trained model evaluation (ROC-AUC, Precision, Confusion Matrix).
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_active_user
from app.evaluation.ai_evaluator import AIEvaluationService
from app.evaluation.ml_evaluator import MLEvaluationService
from app.users.models import User

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/ai", summary="Get AI system evaluation metrics")
async def get_ai_evaluation(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Retrieve RAG faithfulness, answer relevance, retrieval MRR, and agent metrics."""
    return await AIEvaluationService.get_comprehensive_evaluation()


@router.post("/ai/run", summary="Trigger live AI benchmark execution")
async def run_ai_evaluation(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Execute live benchmark suite across RAG engine and Agent workflows."""
    return await AIEvaluationService.get_comprehensive_evaluation()


@router.get("/ml", summary="Get trained ML model evaluation metrics")
async def get_ml_evaluation(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Retrieve empirical model metrics (Precision, Recall, ROC-AUC, FPR, FNR, Confusion Matrix)."""
    return MLEvaluationService.get_metrics()


@router.get("/summary", summary="Get consolidated AI and ML evaluation summary")
async def get_evaluation_summary(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Provide a unified view of both ML predictive performance and AI RAG/Agent benchmarks."""
    ml_metrics = MLEvaluationService.get_metrics()
    ai_metrics = await AIEvaluationService.get_comprehensive_evaluation()
    return {
        "ml": ml_metrics,
        "ai": ai_metrics,
    }
