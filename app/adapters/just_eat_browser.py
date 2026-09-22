"""Adaptador Playwright para obtener el estado SSR de Just Eat España."""

import json

from playwright.sync_api import Error, Page, TimeoutError, sync_playwright

from app.just_eat import CrawlError, MenuSource, validate_url


USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"
)


def read_page(page: Page, url: str, timeout_ms: int = 30000) -> MenuSource:
    url = validate_url(url)
    invalid_redirect = False

    def guard_navigation(route):
        nonlocal invalid_redirect
        if route.request.is_navigation_request() and route.request.frame == page.main_frame:
            try:
                validate_url(route.request.url)
            except CrawlError:
                invalid_redirect = True
                route.abort()
                return
        route.continue_()

    page.route("**/*", guard_navigation)
    try:
        response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        final_url = validate_url(page.url)
        if response is None:
            raise CrawlError("navigation_failed", "La navegación no devolvió una respuesta HTTP.")
        if response.status >= 400:
            code = "access_denied" if response.status in {403, 429} else "http_error"
            raise CrawlError(code, f"Just Eat respondió HTTP {response.status}.")
        raw = page.locator("script#__NEXT_DATA__").text_content(timeout=timeout_ms)
        try:
            document = json.loads(raw)
            if document["props"].get("hasRenderingError"):
                raise ValueError("La página declara un error de renderizado")
            state = document["props"]["appProps"]["preloadedState"]
            cdn = state["menu"]["restaurant"]["cdn"]
            if not isinstance(cdn, dict) or not isinstance(cdn.get("restaurant"), dict) or "httpStatusCode" not in cdn["restaurant"]:
                raise ValueError("No hay catálogo SSR")
            return MenuSource(url=final_url, cdn=cdn,
                              details=state["common"]["menu"]["restaurantInfo"]["restaurant"])
        except (KeyError, TypeError, ValueError) as exc:
            raise CrawlError("unsupported_page", "El estado de la página no contiene el catálogo esperado.") from exc
    except TimeoutError as exc:
        raise CrawlError("timeout", "Se agotó el tiempo de navegación o espera del catálogo.") from exc
    except Error as exc:
        code = "invalid_redirect" if invalid_redirect else "navigation_failed"
        raise CrawlError(code, "Redirección no permitida." if invalid_redirect else "No se pudo cargar la página.") from exc
    finally:
        page.unroute("**/*", guard_navigation)


def fetch_menu(url: str, timeout_ms: int = 30000) -> MenuSource:
    url = validate_url(url)
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(timeout=timeout_ms)
            try:
                context = browser.new_context(locale="es-ES", user_agent=USER_AGENT, service_workers="block")
                return read_page(context.new_page(), url, timeout_ms)
            finally:
                browser.close()
        except Error as exc:
            raise CrawlError("browser_failed", "Chromium no pudo iniciarse o finalizar correctamente.") from exc
