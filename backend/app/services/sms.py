from abc import ABC, abstractmethod
import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class SMSProvider(ABC):
    @abstractmethod
    async def send_code(self, phone: str, code: str) -> bool:
        pass

class MockSMSProvider(SMSProvider):
    """Mock provider for development - logs code to console."""
    
    async def send_code(self, phone: str, code: str) -> bool:
        logger.info(f"[MOCK SMS] Sending code {code} to {phone}")
        print(f"\n{'='*50}")
        print(f"📱 SMS to {phone}")
        print(f"🔐 Your verification code: {code}")
        print(f"{'='*50}\n")
        return True

class TwilioSMSProvider(SMSProvider):
    """Twilio SMS provider for production."""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    
    async def send_code(self, phone: str, code: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    auth=(self.account_sid, self.auth_token),
                    data={
                        "To": phone,
                        "From": self.from_number,
                        "Body": f"Ваш код для Скилл Свап: {code}"
                    }
                )
                return response.status_code == 201
        except Exception as e:
            logger.error(f"Twilio SMS error: {e}")
            return False

class SMSRuProvider(SMSProvider):
    """SMS.ru provider for Russian market."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://sms.ru/sms/send"
    
    async def send_code(self, phone: str, code: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "api_id": self.api_key,
                        "to": phone.replace("+", ""),
                        "msg": f"Ваш код для Скилл Свап: {code}",
                        "json": 1
                    }
                )
                data = response.json()
                return data.get("status") == "OK"
        except Exception as e:
            logger.error(f"SMS.ru error: {e}")
            return False

def get_sms_provider() -> SMSProvider:
    """Factory function to get configured SMS provider."""

    if settings.SMS_PROVIDER != "mock" and settings.SMS_API_KEY is None:
        raise ValueError(f"SMS_API_KEY must be set in .env when SMS_PROVIDER is '{settings.SMS_PROVIDER}'")

    if settings.SMS_PROVIDER == "twilio":

        assert settings.SMS_API_KEY is not None 
             
        parts = settings.SMS_API_KEY.split(":")
        if len(parts) != 3:
            raise ValueError("Twilio SMS_API_KEY format must be: SID:TOKEN:FROM_NUMBER")
            
        return TwilioSMSProvider(parts[0], parts[1], parts[2])
        
    elif settings.SMS_PROVIDER == "mock":
        return MockSMSProvider()
        
    else:
        raise ValueError(f"Unknown SMS provider: {settings.SMS_PROVIDER}")