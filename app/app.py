import reflex as rx
from app.state import AuthState, protected_page
from app.components.navbar import navbar
from app.pages.login import login_page
from app.pages.register import register_page
from app.pages.submit_request import submit_request_page


def home_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(
            rx.el.div(
                rx.el.h1(
                    f"Welcome, {AuthState.current_user.email}!",
                    class_name="text-4xl font-bold text-gray-800",
                ),
                rx.el.p(
                    "You are logged in as a ",
                    rx.el.span(
                        AuthState.current_user["role"]
                        .to_string()
                        .replace("_", " ")
                        .title(),
                        class_name="font-semibold text-blue-600",
                    ),
                    ".",
                    class_name="text-lg text-gray-600 mt-2",
                ),
                rx.cond(
                    AuthState.is_manager,
                    rx.el.div(
                        rx.el.p(
                            "You can now manage all medical requests.",
                            class_name="mt-4 text-gray-500",
                        ),
                        class_name="mt-8 p-6 bg-blue-50 border border-blue-200 rounded-lg",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "You can submit a new medical request from your dashboard.",
                            class_name="mt-4 text-gray-500",
                        ),
                        class_name="mt-8 p-6 bg-gray-50 border border-gray-200 rounded-lg",
                    ),
                ),
                class_name="container mx-auto text-center py-20",
            )
        ),
    )


def index() -> rx.Component:
    return protected_page(home_page())


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, on_load=AuthState.on_load)
app.add_page(login_page, route="/login")
app.add_page(register_page, route="/register")
app.add_page(submit_request_page, route="/submit-request")