"""
ClaimGraph AI — Multimodal Analysis API Router.

Endpoints for inspecting damage imagery, invoice OCR text, and narrative consistency.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from app.multimodal.provider import MultimodalProvider, get_multimodal_provider
from app.multimodal.schemas import MultimodalAnalysisRequest, MultimodalAnalysisResult

router = APIRouter(prefix="/multimodal", tags=["Multimodal Analysis"])


@router.post("/analyze", response_model=MultimodalAnalysisResult)
async def analyze_claim_multimodal(
    request: MultimodalAnalysisRequest,
    provider: MultimodalProvider = Depends(get_multimodal_provider),
) -> MultimodalAnalysisResult:
    """
    Evaluate damage imagery, repair invoices, and claim descriptions.
    Extracts visible damage, checks narrative consistency, and returns corroborating evidence.
    """
    return await provider.analyze(request)
