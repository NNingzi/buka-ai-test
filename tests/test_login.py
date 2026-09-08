from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


def test_admin_can_login(
    credentials,
    login_page: LoginPage,
    dashboard_page: DashboardPage,
) -> None:
    login_page.open()
    login_page.login(credentials.email, credentials.password)

    dashboard_page.expect_loaded_as_admin(credentials.email)
