from decimal import InvalidOperation

from .errors import CrawlError
from .item import to_item
from .source import MenuSource
from .validators import index, list_of, text


def to_venue(source: MenuSource) -> dict:
    """Rechazar un catálogo parcial antes de generar una salida aparentemente completa."""
    try:
        restaurant = source.cdn["restaurant"]
        info = restaurant["restaurantInfo"]
        if restaurant["httpStatusCode"] != 200 or restaurant["countryCode"] != "es":
            raise ValueError("Catálogo no disponible para España")
        restaurant_id = text(restaurant["restaurantId"], "restaurantId")
        if str(source.details["id"]) != restaurant_id:
            raise ValueError("Datos de restaurantes distintos en la misma captura")
        items = source.cdn["items"]
        if not isinstance(items, dict):
            raise ValueError("Catálogo de platos inválido")
        groups = index(list_of(source.cdn["modifierGroups"], "modifierGroups"))
        modifiers = index(list_of(source.cdn["modifierSets"], "modifierSets"))
        menus = {}
        for menu in list_of(restaurant["menus"], "menus"):
            menu_group_id = text(menu["menuGroupId"], "menuGroupId")
            if menu_group_id in menus:
                raise ValueError(f"Menú duplicado: {menu_group_id}")
            menus[menu_group_id] = to_menu(menu, items, restaurant_id, groups, modifiers)
        if not menus:
            raise ValueError("No hay menús")
        location = info["location"]
        coordinates = to_coordinates(location.get("longitude"), location.get("latitude"))
        rating = source.details.get("rating") or {}
        return {
            "name": text(info["name"], "restaurant.name"), "brand": None,
            "uniqueName": text(info["seoName"], "seoName"),
            "address": {"city": location.get("city"), "firstLine": location.get("address"),
                        "postalCode": location.get("postCode"),
                        "location": {"type": "Point", "coordinates": coordinates}},
            "rating": {"count": rating.get("votes"), "starRating": rating.get("score")},
            "logoUrl": info.get("logoUrl"), "isTestRestaurant": info.get("isTestRestaurant"),
            "cuisines": [cuisine["seoName"] for cuisine in list_of(info.get("cuisineTypes", []), "cuisineTypes")],
            "telephone": source.details.get("restaurantPhoneNumber") or None, "ghostStore": None,
            "menus": menus, "description": info.get("description"),
            "openingTimes": info.get("restaurantOpeningTimes", []),
            "storeFrontType": info.get("storeFrontType"), "url": source.url,
        }
    except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
        raise CrawlError("invalid_menu", f"Catálogo incompleto o con formato inesperado: {exc}") from exc


def to_menu(menu: dict, items: dict, restaurant_id: str, groups: dict, modifiers: dict) -> dict:
    menu_group_id = text(menu["menuGroupId"], "menuGroupId")
    service_types = list_of(menu["serviceTypes"], "serviceTypes")
    if not service_types or not all(isinstance(service_type, str) and service_type for service_type in service_types):
        raise ValueError("Tipos de servicio ausentes")
    sections = []
    section_ids = set()
    for category in list_of(menu["categories"], "categories"):
        section_id = text(category["id"], "category.id")
        if section_id in section_ids:
            raise ValueError(f"Sección duplicada: {section_id}")
        section_ids.add(section_id)
        sections.append(to_section(category, menu_group_id, items, restaurant_id, groups, modifiers))
    if not sections or not any(section["items"] for section in sections):
        raise ValueError(f"Menú vacío: {menu_group_id}")
    return {"menuGroupId": menu_group_id, "type": service_types,
            "description": menu.get("description") or "", "sections": sections}


def to_section(category: dict, menu_group_id: str, items: dict, restaurant_id: str, groups: dict, modifiers: dict) -> dict:
    section_id = text(category["id"], "category.id")
    dish_ids = list_of(category["itemIds"], "itemIds")
    if len(dish_ids) != len(set(dish_ids)):
        raise ValueError(f"Referencias de platos duplicadas: {section_id}")
    dishes = []
    for dish_id in dish_ids:
        if dish_id not in items or items[dish_id]["id"] != dish_id:
            raise ValueError(f"Plato referenciado ausente o inconsistente: {dish_id}")
        dishes.append(to_item(items[dish_id], menu_group_id, restaurant_id, groups, modifiers))
    return {"id": section_id, "name": text(category["name"], "category.name"),
            "description": category.get("description") or "", "items": dishes}


def to_coordinates(longitude: object, latitude: object) -> list | None:
    if longitude is None and latitude is None:
        return None
    if (type(longitude) not in (int, float) or type(latitude) not in (int, float)
            or not -180 <= longitude <= 180 or not -90 <= latitude <= 90):
        raise ValueError("Coordenadas inválidas")
    return [longitude, latitude]
