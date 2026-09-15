from __future__ import annotations

import re

from playwright.sync_api import Page, expect


class LoginPage:
    """登录页的元素定位和用户操作。"""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.auth = page.locator("#auth")
        self.form = page.locator("#auth-form")
        self.email_input = self.form.locator('input[name="email"]')
        self.password_input = self.form.locator('input[name="password"]')
        self.submit_button = self.form.locator("#auth-submit")
        self.message = page.locator("#auth-msg")

    def open(self) -> None:
        self.page.goto("/", wait_until="domcontentloaded")
        expect(self.form).to_be_visible()

    def login(self, email: str, password: str) -> None:
        self.fill(email=email, password=password)
        self.submit()

    def fill(self, email: str = "", password: str = "") -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)

    def submit(self) -> None:
        self.submit_button.click()

    def expect_visible(self) -> None:
        expect(self.auth).to_be_visible()
        expect(self.form).to_be_visible()

    def expect_login_failed(self) -> str:
        expect(self.auth).to_be_visible()
        expect(self.message).to_have_class(re.compile(r"\berr\b"))
        expect(self.message).to_have_text(re.compile(r"\S+"))
        return self.message.inner_text().strip()

    def validation_state(self, field: str) -> dict[str, bool | str]:
        fields = {
            "email": self.email_input,
            "password": self.password_input,
        }
        if field not in fields:
            raise ValueError(f"不支持的字段: {field}")
        return fields[field].evaluate(
            """element => ({
                valueMissing: element.validity.valueMissing,
                typeMismatch: element.validity.typeMismatch,
                valid: element.validity.valid,
                message: element.validationMessage
            })"""
        )
