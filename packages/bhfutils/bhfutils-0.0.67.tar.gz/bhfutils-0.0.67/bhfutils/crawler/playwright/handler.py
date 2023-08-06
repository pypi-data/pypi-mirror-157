import asyncio
import logging

from time import time

from .. import bhf_signals
from contextlib import suppress
from inspect import isawaitable
from ipaddress import ip_address
from bhfutils.crawler.playwright.stealth import stealth_async
from typing import Callable, Dict, Generator, Optional, Tuple, Type, TypeVar

from playwright.async_api import (
    BrowserContext,
    Page,
    PlaywrightContextManager,
    Request as PlaywrightRequest,
    Response as PlaywrightResponse,
    Route,
)
from scrapy import Spider, signals
from scrapy.crawler import Crawler
from scrapy.http import Request, Response
from scrapy.http.headers import Headers
from scrapy.utils.misc import load_object
from scrapy.utils.python import to_unicode
from scrapy.responsetypes import responsetypes
from scrapy.utils.defer import deferred_from_coro
from scrapy.utils.reactor import verify_installed_reactor
from twisted.internet.defer import Deferred, inlineCallbacks
from scrapy.core.downloader.handlers.http import HTTPDownloadHandler
from w3lib.encoding import html_body_declared_encoding, http_content_type_encoding

from .headers import use_scrapy_headers
from .page import PageMethod

__all__ = ["ScrapyPlaywrightDownloadHandler"]

PlaywrightHandler = TypeVar("PlaywrightHandler", bound="ScrapyPlaywrightDownloadHandler")

logger = logging.getLogger("scrapy-playwright")


def _make_request_logger(context_name: str) -> Callable:
    def _log_request(request: PlaywrightRequest) -> None:
        logger.debug(
            f"[Context={context_name}] Request: <{request.method.upper()} {request.url}> "
            f"(resource type: {request.resource_type}, referrer: {request.headers.get('referer')})"
        )

    return _log_request


def _make_response_logger(context_name: str) -> Callable:
    def _log_request(response: PlaywrightResponse) -> None:
        logger.debug(
            f"[Context={context_name}] Response: <{response.status} {response.url}> "
            f"(referrer: {response.headers.get('referer')})"
        )

    return _log_request


def _get_page_method_result(page: Page, pm: PageMethod):
    try:
        method = getattr(page, pm.method)
    except AttributeError:
        logger.warning(f"Ignoring {repr(pm)}: could not find method")
        return None
    else:
        return method(*pm.args, **pm.kwargs)


class ScrapyPlaywrightDownloadHandler(HTTPDownloadHandler):
    def __init__(self, crawler: Crawler) -> None:
        super().__init__(settings=crawler.settings, crawler=crawler)
        verify_installed_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
        crawler.signals.connect(self._engine_started, signals.engine_started)
        self.stats = crawler.stats

        self.browser_type: str = crawler.settings.get("PLAYWRIGHT_BROWSER_TYPE") or "chromium"
        self.page_load_until: str = crawler.settings.get("PLAYWRIGHT_PAGE_LOAD_UNTIL") or "load"
        self.max_pages_per_context: int = crawler.settings.getint(
            "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT"
        ) or crawler.settings.getint("CONCURRENT_REQUESTS")
        self.launch_options: dict = crawler.settings.getdict("PLAYWRIGHT_LAUNCH_OPTIONS") or {}

        self.default_navigation_timeout: Optional[float] = None
        if "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT" in crawler.settings:
            with suppress(TypeError, ValueError):
                self.default_navigation_timeout = float(
                    crawler.settings.get("PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT")
                )

        if crawler.settings.get("PLAYWRIGHT_PROCESS_REQUEST_HEADERS"):
            self.process_request_headers = load_object(
                crawler.settings["PLAYWRIGHT_PROCESS_REQUEST_HEADERS"]
            )
        else:
            self.process_request_headers = use_scrapy_headers

        self.context_kwargs: dict = crawler.settings.getdict("PLAYWRIGHT_CONTEXTS")
        self.contexts: Dict[str, BrowserContext] = {}
        self.context_semaphores: Dict[str, asyncio.Semaphore] = {
            'default': asyncio.Semaphore(value=self.max_pages_per_context)
        }

        self.abort_request: Optional[Callable[[PlaywrightRequest], bool]] = None
        if crawler.settings.get("PLAYWRIGHT_ABORT_REQUEST"):
            self.abort_request = load_object(crawler.settings["PLAYWRIGHT_ABORT_REQUEST"])

        self.user_agent_rotation_idx = 0
        self.playwright_user_agents: list = crawler.settings.get("PLAYWRIGHT_USER_AGENTS") or []
        crawler.signals.connect(self._ip_changed, bhf_signals.ip_changed)

    @classmethod
    def from_crawler(cls: Type[PlaywrightHandler], crawler: Crawler) -> PlaywrightHandler:
        return cls(crawler)

    def _engine_started(self) -> Deferred:
        """Launch the browser. Use the engine_started signal as it supports returning deferreds."""
        if not self.playwright_user_agents:
            return deferred_from_coro(self._launch_browser())
        else:
            return deferred_from_coro(self._launch_browser(user_agent=self.playwright_user_agents[1]))

    def _ip_changed(self) -> Deferred:
        """Plan User-Agent rotation"""
        return deferred_from_coro(self._plan_user_agent_rotation())

    async def _launch_browser(self, user_agent=None) -> None:
        self.playwright_context_manager = PlaywrightContextManager()
        self.playwright = await self.playwright_context_manager.start()
        logger.info("Launching browser")
        browser_launcher = getattr(self.playwright, self.browser_type).launch
        self.browser = await browser_launcher(**self.launch_options)
        logger.info(f"Browser {self.browser_type} launched")
        context_kwargs = self.context_kwargs
        if user_agent is not None:
            context_kwargs['user_agent'] = user_agent
        self.contexts = {
            'default': await self._create_browser_context('default', context_kwargs)
        }

    async def _create_browser_context(self, name: str, context_kwargs: dict) -> BrowserContext:
        context = await self.browser.new_context(**context_kwargs)
        context.on("close", self._make_close_browser_context_callback(name))
        logger.debug("Browser context started: '%s'", name)
        self.stats.inc_value("playwright/context_count")
        if self.default_navigation_timeout is not None:
            context.set_default_timeout(self.default_navigation_timeout)
            context.set_default_navigation_timeout(self.default_navigation_timeout)
        return context

    async def _plan_user_agent_rotation(self) -> None:
        logger.info("Re create browser: Before acquire")
        await self.context_semaphores['default'].acquire()
        logger.info("Re create browser: After acquire")

        await self._close()
        if not self.playwright_user_agents:
            await self._launch_browser()
        else:
            logger.info(f"Re create browser with new user-agent: "
                        f"{self.playwright_user_agents[self.user_agent_rotation_idx]}")
            await self._launch_browser(user_agent=self.playwright_user_agents[self.user_agent_rotation_idx])
            self.user_agent_rotation_idx = self.user_agent_rotation_idx + 1
            if self.user_agent_rotation_idx >= len(self.playwright_user_agents):
                self.user_agent_rotation_idx = 0

        if self.context_semaphores['default'].locked():
            self.context_semaphores['default'].release()
        logger.info("Re create browser: Completed")

    async def _create_page(self) -> Page:
        """Create a new page in a context, also creating a new context if necessary."""
        context = self.contexts.get("default")

        page = await context.new_page()
        await stealth_async(page)
        self.stats.inc_value("playwright/page_count")
        logger.debug(
            "[Context=%s] New page created, page count is %i (%i for all contexts)",
            "default",
            len(context.pages),
            self._get_total_page_count(),
        )
        if self.default_navigation_timeout is not None:
            page.set_default_timeout(self.default_navigation_timeout)
            page.set_default_navigation_timeout(self.default_navigation_timeout)

        page.on("request", _make_request_logger("default"))
        page.on("response", _make_response_logger("default"))
        page.on("request", self._increment_request_stats)
        page.on("response", self._increment_response_stats)

        return page

    def _get_total_page_count(self):
        count = sum([len(context.pages) for context in self.contexts.values()])
        current_max_count = self.stats.get_value("playwright/page_count/max_concurrent")
        if current_max_count is None or count > current_max_count:
            self.stats.set_value("playwright/page_count/max_concurrent", count)
        return count

    @inlineCallbacks
    def close(self) -> Deferred:
        yield super().close()
        yield deferred_from_coro(self._close())
        self.context_semaphores.clear()

    async def _close(self) -> None:
        self.contexts.clear()
        if getattr(self, "browser", None):
            logger.info("Closing browser")
            await self.browser.close()
        await self.playwright_context_manager.__aexit__()

    def download_request(self, request: Request, spider: Spider) -> Deferred:
        if request.meta.get("playwright"):
            return deferred_from_coro(self._download_request(request, spider))
        return super().download_request(request, spider)

    async def _download_request(self, request: Request, spider: Spider) -> Response:
        page = None
        try:
            logger.info(f"[{request.url}] Before acquire")
            await self.context_semaphores['default'].acquire()
            logger.info(f"[{request.url}] After acquire")
            page = await self._create_page()

            # attach event handlers
            event_handlers = request.meta.get("playwright_page_event_handlers") or {}
            for event, handler in event_handlers.items():
                if callable(handler):
                    page.on(event, handler)
                elif isinstance(handler, str):
                    try:
                        page.on(event, getattr(spider, handler))
                    except AttributeError:
                        logger.warning(
                            f"Spider '{spider.name}' does not have a '{handler}' attribute,"
                            f" ignoring handler for event '{event}'"
                        )

            await page.unroute("**")
            await page.route(
                "**",
                self._make_request_handler(
                    method=request.method,
                    scrapy_headers=request.headers,
                    body=request.body,
                    encoding=getattr(request, "encoding", None),
                ),
            )

            result = await self._download_request_with_page(request, page)
        except:
            logger.exception(f"[{request.url}] Error while downloading request")
            return Response('', status=504)
        else:
            return result
        finally:
            try:
                if page is not None and not page.is_closed():
                    try:
                        await asyncio.wait_for(page.close(), timeout=10)
                    except asyncio.TimeoutError:
                        if self.context_semaphores['default'].locked():
                            self.context_semaphores['default'].release()
                        await self._plan_user_agent_rotation()
                    else:
                        if self.context_semaphores['default'].locked():
                            self.context_semaphores['default'].release()
                else:
                    if self.context_semaphores['default'].locked():
                        self.context_semaphores['default'].release()
            except:
                logger.exception(f"[{request.url}] Error on page close")
                raise

    async def _download_request_with_page(self, request: Request, page: Page) -> Response:
        start_time = time()
        response = await page.goto(request.url, wait_until=self.page_load_until)

        logger.info(f"[{request.url}] After goto")
        await self._apply_page_methods(page, request)

        logger.info(f"[{request.url}] After apply page methods")
        body_str = await page.content()
        request.meta["download_latency"] = time() - start_time

        server_ip_address = None
        with suppress(AttributeError, KeyError, ValueError):
            server_addr = await response.server_addr()
            if server_addr is not None:
                server_ip_address = ip_address(server_addr.ipAddress)

        with suppress(AttributeError):
            request.meta["playwright_security_details"] = await response.security_details()

        headers = Headers(response.headers)
        headers.pop("Content-Encoding", None)
        body, encoding = _encode_body(headers=headers, text=body_str)
        respcls = responsetypes.from_args(headers=headers, url=page.url, body=body)
        return respcls(
            url=page.url,
            status=response.status,
            headers=headers,
            body=body,
            request=request,
            flags=["playwright"],
            encoding=encoding,
            ip_address=server_ip_address,
        )

    async def _apply_page_methods(self, page: Page, request: Request) -> None:
        page_methods = request.meta.get("playwright_page_methods") or ()

        if isinstance(page_methods, dict):
            page_methods = page_methods.values()
        for pm in page_methods:
            if isinstance(pm, dict):
                pm_group = pm.popitem()
                pm_group_name = pm_group[0]
                pm_group_items = pm_group[1]
                if pm_group_name == 'wait_for_any':
                    timeouts = 0
                    group_length = len(pm_group_items)
                    for pgi in pm_group_items:
                        result = _get_page_method_result(page, pgi)
                        if result is not None:
                            try:
                                pgi.result = await result if isawaitable(result) else result
                                await page.wait_for_load_state(timeout=self.default_navigation_timeout)
                                return
                            except Exception:
                                timeouts += 1
                                if timeouts == group_length:
                                    raise
                                else:
                                    logger.warning(f"Ignoring TimeoutError {timeouts} time")
            elif isinstance(pm, PageMethod):
                result = _get_page_method_result(page, pm)
                if result is not None:
                    pm.result = await result if isawaitable(result) else result
                    await page.wait_for_load_state(timeout=self.default_navigation_timeout)
            else:
                logger.warning(f"Ignoring {repr(pm)}: expected PageMethod, got {repr(type(pm))}")

    def _increment_request_stats(self, request: PlaywrightRequest) -> None:
        stats_prefix = "playwright/request_count"
        self.stats.inc_value(stats_prefix)
        self.stats.inc_value(f"{stats_prefix}/resource_type/{request.resource_type}")
        self.stats.inc_value(f"{stats_prefix}/method/{request.method}")
        if request.is_navigation_request():
            self.stats.inc_value(f"{stats_prefix}/navigation")

    def _increment_response_stats(self, response: PlaywrightResponse) -> None:
        stats_prefix = "playwright/response_count"
        self.stats.inc_value(stats_prefix)
        self.stats.inc_value(f"{stats_prefix}/resource_type/{response.request.resource_type}")
        self.stats.inc_value(f"{stats_prefix}/method/{response.request.method}")

    def _make_close_page_callback(self, context_name: str) -> Callable:
        def close_page_callback() -> None:
            if context_name in self.context_semaphores and self.context_semaphores[context_name].locked():
                self.context_semaphores[context_name].release()

        return close_page_callback

    def _make_close_browser_context_callback(self, name: str) -> Callable:
        def close_browser_context_callback() -> None:
            logger.debug("Browser context closed: '%s'", name)
            if name in self.contexts:
                self.contexts.pop(name)

        return close_browser_context_callback

    def _make_request_handler(
            self, method: str, scrapy_headers: Headers, body: Optional[bytes], encoding: str = "utf8"
    ) -> Callable:
        async def _request_handler(route: Route, playwright_request: PlaywrightRequest) -> None:
            """Override request headers, method and body."""
            if self.abort_request and self.abort_request(playwright_request):
                await route.abort()
                self.stats.inc_value("playwright/request_count/aborted")
                return None

            processed_headers = await self.process_request_headers(
                self.browser_type, playwright_request, scrapy_headers
            )

            # the request that reaches the callback should contain the headers that were sent
            scrapy_headers.clear()
            scrapy_headers.update(processed_headers)

            overrides: dict = {"headers": processed_headers}
            if playwright_request.is_navigation_request():
                overrides["method"] = method
                if body is not None:
                    overrides["post_data"] = body.decode(encoding)

            await route.continue_(**overrides)

        return _request_handler


def _possible_encodings(headers: Headers, text: str) -> Generator[str, None, None]:
    if headers.get("content-type"):
        content_type = to_unicode(headers["content-type"])
        yield http_content_type_encoding(content_type)
    yield html_body_declared_encoding(text)


def _encode_body(headers: Headers, text: str) -> Tuple[bytes, str]:
    for encoding in filter(None, _possible_encodings(headers, text)):
        try:
            body = text.encode(encoding)
        except UnicodeEncodeError:
            pass
        else:
            return body, encoding
    return text.encode("utf-8"), "utf-8"  # fallback
