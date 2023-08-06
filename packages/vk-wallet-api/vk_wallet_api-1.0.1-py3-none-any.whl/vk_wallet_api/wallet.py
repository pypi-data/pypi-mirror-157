import json
import aiohttp
import hashlib
from typing import Any
from datetime import datetime

from .schemes import HttpMethod, UserBalance, PaymentUrl, \
    TranslationType, Translation, SendCoins, \
    SetCallback, DeleteCallback


class Wallet:

    def __init__(self, access_token: str) -> None:
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    @staticmethod
    def validate_datetime(date_time: str) -> datetime:
        """Парсит datetime"""

        return datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")


    async def method(
            self, http_method: HttpMethod,
            method: str, **kwargs
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Вызов метода WALLET API"""
        request_url = f"http://188.120.237.213/payment_system/api/{method}"

        async with aiohttp.ClientSession() as session:
            if http_method == HttpMethod.GET:
                session = session.get
            elif http_method == HttpMethod.POST:
                session = session.post
            elif http_method == HttpMethod.DELETE:
                session = session.delete

            response = await session(url=request_url, headers=self.headers, **kwargs)
            response = await response.json()

            return response


    async def get_balance(self) -> UserBalance:
        """Получение баланса"""

        return UserBalance(**(await self.method(HttpMethod.GET, "balance")))


    async def get_payment_url(self, payload=None) -> PaymentUrl:
        """Получение ссылки на оплату"""
        params = {}

        if payload:
            params["payload"] = payload

        return PaymentUrl(**(await self.method(HttpMethod.GET, "payment_url", params=params)))


    async def get_transactions(
            self, type: TranslationType = TranslationType.ALL,
            offset: int = 0, limit: int = 20
    ) -> list[Translation]:
        """Возвращает список последних транзакций"""

        params = {
            "type": type.value,
            "offset": offset,
            "limit": limit
        }

        transactions = []

        for transaction in await self.method(HttpMethod.GET, "transactions", params=params):
            transaction["created_at"] = Wallet.validate_datetime(transaction["created_at"])
            transactions.append(Translation(**transaction))

        return transactions


    async def get_last_transaction_id(self) -> int:
        """Получение идентификатора последней транзакции"""

        transactions = await self.get_transactions()

        return transactions[0].id if len(transactions) > 0 else 0


    async def checks_user_exists(self, user_id: int) -> bool:
        """Проверяет зарегистрирован ли пользователь в wallet"""
        params = {"check_id": user_id}

        return (await self.method(HttpMethod.GET, "checks_user_exists", params=params))["exists"]


    async def send_coins(
        self, recipient_id: int,
        amount: float, payload: str | None = None
    ) -> SendCoins:
        """Переводит coins пользователю"""

        data = {
            "recipient_id": recipient_id,
            "amount": amount
        }

        if payload:
            data["payload"] = payload

        send_coins_date = await self.method(HttpMethod.POST, "send_coins", data=json.dumps(data))
        send_coins_date["created_at"] = Wallet.validate_datetime(send_coins_date["created_at"])

        return SendCoins(**send_coins_date)


    async def set_callback_address(self, callback_url: str) -> SetCallback:
        """Устанавливает callback для получения уведомления о переводах"""

        data = {"url": callback_url}

        return SetCallback(**(await self.method(HttpMethod.POST, "callback", data=json.dumps(data))))


    async def delete_callback(self) -> DeleteCallback:
        """Удаляет callback у пользователя"""

        return DeleteCallback(**(await self.method(HttpMethod.DELETE, "callback")))


    @staticmethod
    async def validate_sing(transaction: dict, callback_secret: str) -> bool:
        """Валидация callback-данных"""

        received_sign = transaction["sign"]
        del transaction["sign"]

        items = []
        for key in sorted(transaction.keys()):
            items.append(f"{key}={transaction[key]}")

        result = "&".join(items) + f"&{callback_secret}"
        return hashlib.md5(result.encode()).hexdigest() == received_sign
