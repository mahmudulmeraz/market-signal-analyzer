"""Official-API broker adapter. No unofficial automation is implemented."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BrokerAdapter(ABC):
    @abstractmethod
    def connect(self) -> bool: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]: ...

    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]: ...

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool: ...


class UnconfiguredBroker(BrokerAdapter):
    def connect(self) -> bool:
        return False

    def disconnect(self) -> None:
        return None

    def get_account_info(self) -> Dict[str, Any]:
        return {"status": "NOT CONFIGURED", "note": "Research + paper trading only"}

    def get_positions(self) -> List[Dict[str, Any]]:
        return []

    def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        raise RuntimeError("No official broker API is configured. Paper trading only.")

    def cancel_order(self, order_id: str) -> bool:
        return False
