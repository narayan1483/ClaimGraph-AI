"""
ClaimGraph AI — Common schemas tests.
"""

from __future__ import annotations

from app.common.schemas import PaginationParams, SuccessResponse


def test_pagination_offset() -> None:
    """Offset should be (page - 1) * page_size."""
    params = PaginationParams(page=3, page_size=20)
    assert params.offset == 40


def test_pagination_defaults() -> None:
    """Default pagination should be page=1, page_size=20."""
    params = PaginationParams()
    assert params.page == 1
    assert params.page_size == 20
    assert params.offset == 0


def test_success_response_wrapping() -> None:
    """SuccessResponse should wrap arbitrary data."""
    resp = SuccessResponse[dict](data={"id": "abc"}, message="Created")
    assert resp.success is True
    assert resp.data["id"] == "abc"
    assert resp.message == "Created"
