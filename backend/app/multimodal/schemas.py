"""
ClaimGraph AI — Multimodal Analysis Schemas.

Pydantic schemas for vision, invoice document, and damage claim consistency analysis.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MultimodalAnalysisRequest(BaseModel):
    """Payload for multimodal analysis."""

    claim_id: Optional[str] = None
    claim_description: str = Field(..., min_length=5, description="Claimant's description of the incident")
    claim_amount: Optional[float] = None
    device_serial: Optional[str] = None
    incident_date: Optional[str] = None
    invoice_text: Optional[str] = Field(None, description="Extracted OCR text or invoice details")
    image_path_or_url: Optional[str] = Field(None, description="Path or URL to damage photograph")


class DocumentExtractedInfo(BaseModel):
    """Structured information extracted from repair/purchase invoice."""

    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    total_amount: Optional[float] = None
    serial_number_match: bool = True
    authorized_vendor: bool = True
    items: List[str] = Field(default_factory=list)


class DamageVisionInfo(BaseModel):
    """Visual observation from photographic inspection."""

    visible_damage: List[str] = Field(default_factory=list)
    image_summary: str
    severity: str = "MODERATE"  # MINOR, MODERATE, SEVERE, TOTAL_LOSS
    point_of_impact: Optional[str] = None
    visual_authenticity: str = "GENUINE"  # GENUINE, SUSPICIOUS, UNVERIFIED


class MultimodalAnalysisResult(BaseModel):
    """Consolidated multimodal analysis results with consistency checks."""

    claim_id: Optional[str] = None
    visible_damage: List[str] = Field(default_factory=list)
    image_summary: str
    document_information: Dict[str, Any] = Field(default_factory=dict)
    invoice_information: Dict[str, Any] = Field(default_factory=dict)
    claim_description_consistency: bool = True
    consistency_rationale: str
    possible_inconsistencies: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    provider: str
    evidence_disclaimer: str = (
        "Vision analysis provides corroborating evidence only. "
        "Photographic assessment alone does not conclusively prove or disprove fraud."
    )
