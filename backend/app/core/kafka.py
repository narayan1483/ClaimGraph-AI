"""
ClaimGraph AI — Kafka Infrastructure.

Provides async Kafka producer and consumer lifecycle management with
graceful non-blocking fallbacks when the broker is unavailable.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_kafka_producer: AIOKafkaProducer | None = None
_kafka_available: Optional[bool] = None

# Standard ClaimGraph AI Event Topics
TOPIC_CLAIM_CREATED = "claim.created"
TOPIC_DOCUMENT_UPLOADED = "document.uploaded"
TOPIC_IMAGE_UPLOADED = "image.uploaded"
TOPIC_FRAUD_ANALYSIS_COMPLETED = "fraud.analysis.completed"
TOPIC_GRAPH_ANALYSIS_COMPLETED = "graph.analysis.completed"
TOPIC_AI_INVESTIGATION_COMPLETED = "ai.investigation.completed"
TOPIC_CLAIM_REVIEWED = "claim.reviewed"
TOPIC_CLAIM_APPROVED = "claim.approved"
TOPIC_CLAIM_REJECTED = "claim.rejected"


async def get_kafka_producer() -> Optional[AIOKafkaProducer]:
    """Return the shared Kafka producer, or None if broker is offline."""
    global _kafka_producer, _kafka_available
    if _kafka_available is False:
        return None

    if _kafka_producer is None:
        settings = get_settings()
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: v.encode("utf-8") if isinstance(v, str) else v,
            request_timeout_ms=500,
        )
        try:
            # Fast non-blocking timeout for local/test environments
            await asyncio.wait_for(producer.start(), timeout=0.3)
            _kafka_producer = producer
            _kafka_available = True
            logger.info("kafka_producer_started", servers=settings.kafka_bootstrap_servers)
        except Exception as exc:
            _kafka_available = False
            _kafka_producer = None
            logger.debug("kafka_broker_offline", error=str(exc))
            return None

    return _kafka_producer


async def close_kafka_producer() -> None:
    """Gracefully stop the Kafka producer."""
    global _kafka_producer, _kafka_available
    if _kafka_producer is not None:
        try:
            await _kafka_producer.stop()
        except Exception:
            pass
        _kafka_producer = None
    _kafka_available = None


def create_kafka_consumer(
    *topics: str,
    group_id: str | None = None,
) -> AIOKafkaConsumer:
    """Create a Kafka consumer for the given topics."""
    settings = get_settings()
    return AIOKafkaConsumer(
        *topics,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=group_id or settings.kafka_group_id,
        auto_offset_reset=settings.kafka_auto_offset_reset,
        value_deserializer=lambda v: v.decode("utf-8"),
    )


async def publish_kafka_event(topic: str, payload: Dict[str, Any]) -> bool:
    """Publish an event to a Kafka topic. Gracefully no-ops when Kafka is offline."""
    try:
        producer = await get_kafka_producer()
        if producer is None:
            return False
        payload_bytes = json.dumps(payload, default=str).encode("utf-8")
        await asyncio.wait_for(producer.send_and_wait(topic, payload_bytes), timeout=0.5)
        logger.debug("kafka_event_published", topic=topic, keys=list(payload.keys()))
        return True
    except Exception as exc:
        logger.debug("kafka_publish_skipped", topic=topic, error=str(exc))
        return False


async def kafka_health_check() -> bool:
    """Return True if the Kafka producer can connect to the cluster."""
    try:
        producer = await get_kafka_producer()
        if producer is None:
            return False
        return producer.client.cluster is not None
    except Exception as exc:
        logger.debug("kafka_health_check_failed", error=str(exc))
        return False
