import unittest

from app.classification.domain.rules import classify
from tests.sources.classification import category, dish, taxonomy


class ClassificationRulesTest(unittest.TestCase):
    def test_classifies_an_alias_found_in_the_dish_name(self):
        result = classify(dish("Hamburguesa completa"), taxonomy(category("burger")))

        self.assertEqual(result.status, "classified")
        self.assertEqual(result.category.name, "burger")
        self.assertEqual(result.rule, "AliasRule")

    def test_uses_the_section_for_a_generic_category(self):
        result = classify(dish("Selección de la casa", section="Postres"),
                          taxonomy(category("generic sweets", generic=True, parent="sweets")))

        self.assertEqual(result.status, "classified")
        self.assertEqual(result.category.name, "generic sweets")
        self.assertEqual(result.rule, "SectionRule")

    def test_does_not_classify_an_unknown_dish(self):
        result = classify(dish("Especialidad del chef"), taxonomy(category("burger")))

        self.assertEqual(result.status, "review")
        self.assertIsNone(result.category)
        self.assertEqual(result.rule, "insufficient_evidence")

    def test_prioritizes_the_dish_name_over_an_ingredient_in_description(self):
        result = classify(dish("Ensalada César", description="Con pollo a la plancha"),
                          taxonomy(category("salads"), category("chicken")))

        self.assertEqual(result.category.name, "salads")
        self.assertEqual(result.rule, "AliasRule")

    def test_does_not_match_a_short_alias_inside_another_word(self):
        result = classify(dish("Focaccia", section="Entrantes"), taxonomy(category("tea")))

        self.assertEqual(result.status, "review")

    def test_uses_restaurant_cuisine_only_with_a_dish_signal(self):
        result = classify(dish("Maki especial", cuisines=("japonesa",)), taxonomy(category("sushi")))

        self.assertEqual(result.category.name, "sushi")
        self.assertEqual(result.rule, "RestaurantCuisineRule")

    def test_classifies_a_dish_from_a_plural_section_name(self):
        result = classify(dish("Margarita", section="Pizzas"), taxonomy(category("pizza")))

        self.assertEqual(result.category.name, "pizza")
        self.assertEqual(result.rule, "SectionRule")

    def test_normalizes_catalan_section_to_a_generic_parent_category(self):
        result = classify(dish("Agua", section="Begudes"),
                          taxonomy(category("other drink", generic=True, parent="other drink")))

        self.assertEqual(result.category.name, "other drink")
        self.assertEqual(result.rule, "SectionRule")

    def test_normalizes_english_section_to_its_category(self):
        result = classify(dish("Reserva", section="Red Wines"), taxonomy(category("tintos")))

        self.assertEqual(result.category.name, "tintos")
        self.assertEqual(result.rule, "SectionRule")

    def test_normalizes_plural_specialty_section_to_its_category(self):
        result = classify(dish("Oferta 1", section="Durums"), taxonomy(category("kebab")))

        self.assertEqual(result.category.name, "kebab")

    def test_classifies_a_multilingual_dish_alias(self):
        result = classify(dish("Macarrons bolonyesa"), taxonomy(category("pasta varieties")))

        self.assertEqual(result.category.name, "pasta varieties")
        self.assertEqual(result.rule, "AliasRule")

    def test_does_not_classify_an_unknown_dish_from_cuisine_alone(self):
        result = classify(dish("Especialidad de la casa", cuisines=("japonesa",)), taxonomy(category("sushi")))

        self.assertEqual(result.status, "review")
