from typing import Any


mock_invalid_inventory_data: dict[str, Any] = {
    "organizationUuid": "50e8400-e29b-41d4-a716-446655440000",
    "messageUuid": "550e8400-e29b-41d4-a716-446655440001",
    "eventName": "inventory.balance.updated",
    "messageId": "550e8400-e29b-41d4-a716-446655440002",
    "payload": {
        "organizationUuid": "550e8400-e29b-41d4-a716-446655440000",
        "updated": {
            "uuid": "550e8400-e29b-41d4-a716-446655440003",
            "timestamp": "2026-09-17T09:30:00Z",
            "userType": "system",
            "clientUuid": "550e8400-e29b-41d4-a716-446655440004",
        },
        "balanceBefore": [
            {
                "organizationUuid": "",
                "locationUuid": "550e8400-e29b-41d4-a716-446655440005",
                "productUuid": "550e8400-e29b-41d4-a716-446655440006",
                "variantUuid": "550e8400-e29b-41d4-a716-446655440007",
                "balance": '10',
            }
        ],
        "balanceAfter": [
            {
                "organizationUuid": "550e8400-e29b-41d4-a716-446655440000",
                "locationUuid": "550e8400-e29b-41d4-a716-446655440005",
                "productUuid": "550e8400-e29b-41d4-a716-446655440006",
                "variantUuid": "550e8400-e29b-41d4-a716-446655440007",
                "balance": 15,
            }
        ],
        "externalUuid": None,
    },
    "timestamp": "2026-09-17T09:30:00Z",
}

mock_valid_inventory_data:dict[str, Any] = {
    "organizationUuid": "550e8400-e29b-41d4-a716-446655440000",
    "messageUuid": "550e8400-e29b-41d4-a716-446655440001",
    "eventName": "inventory.balance.updated",
    "messageId": "550e8400-e29b-41d4-a716-446655440002",
    "payload": {
        "organizationUuid": "550e8400-e29b-41d4-a716-446655440000",
        "updated": {
            "uuid": "550e8400-e29b-41d4-a716-446655440003",
            "timestamp": "2026-09-17T09:30:00Z",
            "userType": "system",
            "clientUuid": "550e8400-e29b-41d4-a716-446655440004",
        },
        "balanceBefore": [
            {
                "organizationUuid": "550e8400-e29b-41d4-a716-446655440000",
                "locationUuid": "550e8400-e29b-41d4-a716-446655440005",
                "productUuid": "550e8400-e29b-41d4-a716-446655440006",
                "variantUuid": "550e8400-e29b-41d4-a716-446655440007",
                "balance": 10,
            }
        ],
        "balanceAfter": [
            {
                "organizationUuid": "550e8400-e29b-41d4-a716-446655440000",
                "locationUuid": "550e8400-e29b-41d4-a716-446655440005",
                "productUuid": "550e8400-e29b-41d4-a716-446655440006",
                "variantUuid": "550e8400-e29b-41d4-a716-446655440007",
                "balance": 15,
            }
        ],
        "externalUuid": None,
    },
    "timestamp": "2026-09-17T09:30:00Z"
}