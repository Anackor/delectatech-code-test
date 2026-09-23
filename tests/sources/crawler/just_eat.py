"""Fuentes reutilizables del contrato SSR observado de Just Eat."""

from app.crawler.adapters.just_eat.mapper import to_venue
from app.crawler.adapters.just_eat.source import MenuSource
from app.crawler.application.models import CrawlCapture


def menu_source() -> MenuSource:
    return MenuSource(
        url="https://www.just-eat.es/restaurants-demo/menu",
        details={"id": "42", "rating": {"votes": 3, "score": 4.5}, "restaurantPhoneNumber": "600000000"},
        cdn={
            "restaurant": {
                "httpStatusCode": 200, "countryCode": "es", "restaurantId": "42", "menuVersion": "v1",
                "restaurantInfo": {
                    "name": "Demo", "seoName": "demo", "description": "Carta de prueba", "logoUrl": None,
                    "isTestRestaurant": False, "cuisineTypes": [{"seoName": "pizza"}],
                    "location": {"city": "Barcelona", "address": "Calle Uno, 1", "postCode": "08001", "longitude": 2.1, "latitude": 41.3},
                    "restaurantOpeningTimes": [], "storeFrontType": "Restaurant",
                },
                "menus": [{
                    "menuGroupId": "delivery", "serviceTypes": ["delivery"], "description": "",
                    "categories": [{"id": "starters", "name": "Entrantes", "description": "", "itemIds": ["dish-1", "dish-2"]}],
                }],
            },
            "items": {
                "dish-1": {
                    "id": "dish-1", "name": "Patatas", "description": "", "imageSources": [],
                    "variations": [{"id": "dish-1", "name": "", "basePrice": 3.5, "menuGroupIds": ["delivery"], "modifierGroupsIds": ["extras"], "dealGroupsIds": None}],
                },
                "dish-2": {
                    "id": "dish-2", "name": "Pizza", "description": "Con queso",
                    "imageSources": [{"path": "https://image/{transformations}/pizza", "source": "Cloudinaryv2"}],
                    "variations": [
                        {"id": "small", "name": "Pequeña", "basePrice": 8, "menuGroupIds": ["delivery"], "modifierGroupsIds": [], "dealGroupsIds": None},
                        {"id": "large", "name": "Grande", "basePrice": 10, "menuGroupIds": ["delivery"], "modifierGroupsIds": [], "dealGroupsIds": None},
                    ],
                },
            },
            "modifierGroups": [{"id": "extras", "name": "Extras", "minChoices": 0, "maxChoices": 2, "modifiers": ["extra-1"]}],
            "modifierSets": [{"id": "extra-1", "modifier": {"name": "Salsa", "additionPrice": 0.5}}],
        },
    )


def crawl_capture() -> CrawlCapture:
    source = menu_source()
    return CrawlCapture(url=source.url, menu_version=source.cdn["restaurant"]["menuVersion"], venue=to_venue(source))
