from __future__ import annotations

from playwright.sync_api import Page, expect


class LoginPage:
    """登录页的元素定位和用户操作。"""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.form = page.locator("#auth-form")
        self.email_input = self.form.locator('input[name="email"]')
        self.password_input = self.form.locator('input[name="password"]')
        self.submit_button = self.form.locator("#auth-submit")

    def open(self) -> None:
        self.page.goto("/", wait_until="domcontentloaded")
        expect(self.form).to_be_visible()

    def login(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()
