from __future__ import annotations

import re

from playwright.sync_api import Page, expect


class DashboardPage:
    """登录成功后的仪表盘关键状态。"""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.app = page.locator("#app")
        self.page_title = page.locator("#page-title")
        self.user_email = page.locator("#user-email")
        self.admin_navigation = page.locator("#nav-admin")
        self.logout_button = page.locator("#logout")

    def expect_loaded_as_admin(self, email: str) -> None:
        expect(self.page).to_have_url(re.compile(r"#/dashboard$"))
        expect(self.app).to_be_visible()
        expect(self.page_title).to_have_text("仪表盘")
        expect(self.user_email).to_have_text(email)
        expect(self.admin_navigation).to_be_visible()
        expect(self.logout_button).to_be_visible()
