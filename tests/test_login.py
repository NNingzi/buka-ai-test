from __future__ import annotations

from uuid import uuid4

from playwright.sync_api import Page, expect

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


def _capture_login_requests(page: Page) -> list[str]:
    requests: list[str] = []

    def capture(request) -> None:
        if request.url.endswith("/api/auth/login"):
            requests.append(request.url)

    page.on("request", capture)
    return requests


def test_01_correct_email_and_password_login_successfully(
    credentials,
    login_page: LoginPage,
    dashboard_page: DashboardPage,
) -> None:
    login_page.open()
    login_page.login(credentials.email, credentials.password)

    dashboard_page.expect_loaded_as_admin(credentials.email)


def test_02_correct_email_and_wrong_password_show_error(
    credentials,
    login_page: LoginPage,
) -> None:
    login_page.open()
    wrong_password = f"wrong-{uuid4().hex}"
    login_page.login(credentials.email, wrong_password)

    error_message = login_page.expect_login_failed()
    assert error_message


def test_03_empty_email_is_rejected_by_frontend(
    credentials,
    page: Page,
    login_page: LoginPage,
) -> None:
    login_requests = _capture_login_requests(page)
    login_page.open()
    login_page.fill(password=credentials.password)
    login_page.submit()

    validation = login_page.validation_state("email")
    assert validation["valueMissing"] is True
    assert validation["valid"] is False
    assert validation["message"]
    assert login_requests == []
    expect(login_page.email_input).to_be_focused()


def test_04_empty_password_is_rejected_by_frontend(
    credentials,
    page: Page,
    login_page: LoginPage,
) -> None:
    login_requests = _capture_login_requests(page)
    login_page.open()
    login_page.fill(email=credentials.email)
    login_page.submit()

    validation = login_page.validation_state("password")
    assert validation["valueMissing"] is True
    assert validation["valid"] is False
    assert validation["message"]
    assert login_requests == []
    expect(login_page.password_input).to_be_focused()


def test_05_invalid_email_format_is_rejected_by_frontend(
    credentials,
    page: Page,
    login_page: LoginPage,
) -> None:
    login_requests = _capture_login_requests(page)
    login_page.open()
    login_page.fill(email="not-an-email", password=credentials.password)
    login_page.submit()

    validation = login_page.validation_state("email")
    assert validation["typeMismatch"] is True
    assert validation["valid"] is False
    assert validation["message"]
    assert login_requests == []
    expect(login_page.email_input).to_be_focused()


def test_06_logout_after_login_returns_to_login_page(
    credentials,
    page: Page,
    login_page: LoginPage,
    dashboard_page: DashboardPage,
) -> None:
    login_page.open()
    login_page.login(credentials.email, credentials.password)
    dashboard_page.expect_loaded_as_admin(credentials.email)

    dashboard_page.logout()

    login_page.expect_visible()
    dashboard_page.expect_access_blocked()
    assert page.evaluate("localStorage.getItem('buka_token')") is None


def test_07_unauthenticated_dashboard_access_is_blocked(
    page: Page,
    login_page: LoginPage,
    dashboard_page: DashboardPage,
) -> None:
    dashboard_page.open_directly()

    login_page.expect_visible()
    dashboard_page.expect_access_blocked()
    assert page.evaluate("localStorage.getItem('buka_token')") is None
