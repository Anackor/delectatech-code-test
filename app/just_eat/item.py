from .errors import CrawlError
from .validators import list_of, price, text


def to_item(item: dict, menu_group_id: str, restaurant_id: str, groups: dict, modifiers: dict) -> dict:
    item_id = text(item["id"], "item.id")
    variations = [
        variation for variation in list_of(item["variations"], "variations")
        if menu_group_id in list_of(variation["menuGroupIds"], "menuGroupIds")
    ]
    if not variations:
        raise ValueError(f"Plato sin precio para el menú {menu_group_id}: {item_id}")
    image_sources = list_of(item.get("imageSources", []), "imageSources")
    image = image_sources[0]["path"] if image_sources else None
    if image:
        image = image.replace("{transformations}", "ar_4:3,c_thumb,h_450,w_600/f_auto/q_auto")
    return {
        "id": item_id,
        "name": text(item["name"], "item.name"),
        "description": item.get("description") or "",
        "image": image,
        "imageFilename": f"{restaurant_id}_{item_id}.jpg",
        "price": float(min(price(variation["basePrice"]) for variation in variations)),
        "subSelections": to_subselections(variations, groups, modifiers),
    }


def to_subselections(variations: list, groups: dict, modifiers: dict) -> list:
    selections = []
    group_ids = list_of(variations[0]["modifierGroupsIds"], "modifierGroupsIds")
    if any(variation["modifierGroupsIds"] != group_ids for variation in variations):
        raise CrawlError("unsupported_menu", "Opciones condicionadas a variantes: requieren un contrato más amplio.")
    if any(variation.get("dealGroupsIds") for variation in variations):
        raise CrawlError("unsupported_menu", "Los combos con dealGroups aún no están soportados.")
    if len(variations) > 1:
        base = min(price(variation["basePrice"]) for variation in variations)
        selections.append({
            "name": "Variante", "multipleSelection": False, "minSelection": 1, "maxSelection": 1,
            "options": [
                {"id": text(variation["id"], "variation.id"), "name": text(variation["name"], "variation.name"),
                 "price": float(price(variation["basePrice"]) - base)}
                for variation in variations
            ],
        })
    for group_id in group_ids:
        group = groups[group_id]
        lower, upper = group["minChoices"], group["maxChoices"]
        if type(lower) is not int or type(upper) is not int or not 0 <= lower <= upper:
            raise ValueError(f"Límites de selección inválidos: {group_id}")
        options = [
            {"id": modifier_id, "name": text(modifiers[modifier_id]["modifier"]["name"], "modifier.name"),
             "price": float(price(modifiers[modifier_id]["modifier"]["additionPrice"]))}
            for modifier_id in list_of(group["modifiers"], "modifiers")
        ]
        if not options:
            raise ValueError(f"Grupo de opciones vacío: {group_id}")
        selections.append({
            "name": text(group["name"], "modifierGroup.name"), "multipleSelection": upper > 1,
            "minSelection": lower, "maxSelection": upper, "options": options,
        })
    return selections
