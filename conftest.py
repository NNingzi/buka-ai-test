from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Error as PlaywrightError, Page, Playwright, sync_playwright

from config import PROJECT_ROOT, Settings, settings as project_settings
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
SCREENSHOTS_DIR = ARTIFACTS_DIR / "screenshots"
TRACES_DIR = ARTIFACTS_DIR / "traces"


@dataclass(frozen=True)
class Credentials:
    email: str
    password: str


def pytest_configure() -> None:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    TRACES_DIR.mkdir(parents=True, exist_ok=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def _artifact_name(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", nodeid).strip("_")


@pytest.fixture(scope="session")
def settings() -> Settings:
    return project_settings


@pytest.fixture(scope="session")
def credentials(settings: Settings) -> Credentials:
    if not settings.admin_email or not settings.admin_password:
        pytest.skip("请先从 .env.example 创建 .env，并填写管理员账号和密码")
    return Credentials(settings.admin_email, settings.admin_password)


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, settings: Settings) -> Browser:
    browser = playwright_instance.chromium.launch(headless=settings.headless)
    yield browser
    browser.close()


@pytest.fixture()
def page(request: pytest.FixtureRequest, browser: Browser, settings: Settings) -> Page:
    context = browser.new_context(base_url=settings.base_url)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    page.set_default_timeout(15_000)
    page.set_default_navigation_timeout(30_000)

    yield page

    test_failed = bool(getattr(request.node, "rep_setup", None) and request.node.rep_setup.failed)
    test_failed = test_failed or bool(
        getattr(request.node, "rep_call", None) and request.node.rep_call.failed
    )
    artifact_name = _artifact_name(request.node.nodeid)

    try:
        if test_failed:
            try:
                page.screenshot(
                    path=str(SCREENSHOTS_DIR / f"{artifact_name}.png"),
                    full_page=True,
                )
            except PlaywrightError:
                # 页面可能已崩溃或被关闭；仍继续保存 Trace，保留排查信息。
                pass
            context.tracing.stop(path=str(TRACES_DIR / f"{artifact_name}.zip"))
        else:
            context.tracing.stop()
    finally:
        context.close()


@pytest.fixture()
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture()
def dashboard_page(page: Page) -> DashboardPage:
    return DashboardPage(page)
