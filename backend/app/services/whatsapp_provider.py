from abc import ABC, abstractmethod


class WhatsAppProvider(ABC):
    @abstractmethod
    async def send_message(self, to: str, message: str) -> dict:
        pass

    @abstractmethod
    async def send_template(self, to: str, template_name: str, params: dict) -> dict:
        pass

    @abstractmethod
    async def verify_number(self, phone_number: str) -> bool:
        pass


class MockWhatsAppProvider(WhatsAppProvider):
    async def send_message(self, to: str, message: str) -> dict:
        return {
            "status": "sent",
            "provider": "mock",
            "to": to,
            "message_id": f"mock_{to}_{hash(message) % 100000}",
            "message": message[:50],
        }

    async def send_template(self, to: str, template_name: str, params: dict) -> dict:
        return {
            "status": "sent",
            "provider": "mock",
            "to": to,
            "template": template_name,
            "message_id": f"mock_tmpl_{to}_{hash(template_name) % 100000}",
        }

    async def verify_number(self, phone_number: str) -> bool:
        return len(phone_number) >= 10 and phone_number.startswith("+")


_providers: dict[str, type[WhatsAppProvider]] = {}


def register_provider(name: str, provider_cls: type[WhatsAppProvider]):
    _providers[name] = provider_cls


def get_provider(name: str = "mock") -> WhatsAppProvider:
    if name not in _providers:
        return MockWhatsAppProvider()
    return _providers[name]()


register_provider("mock", MockWhatsAppProvider)
