import reflex as rx
from app.state import AuthState


def navbar() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.a(
                rx.el.div(
                    rx.icon(tag="activity", class_name="w-6 h-6 text-blue-600"),
                    rx.el.span(
                        "MediRequest",
                        class_name="text-xl font-bold text-gray-800 tracking-tighter",
                    ),
                    class_name="flex items-center gap-2",
                ),
                href="/",
            ),
            rx.el.div(
                rx.cond(
                    AuthState.is_authenticated,
                    rx.el.div(
                        rx.cond(
                            ~AuthState.is_manager,
                            rx.el.a(
                                "Submit Request",
                                href="/submit-request",
                                class_name="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors",
                            ),
                        ),
                        rx.el.span(
                            f"Welcome, {AuthState.current_user['email']}",
                            class_name="text-sm font-medium text-gray-600",
                        ),
                        rx.el.button(
                            "Logout",
                            on_click=AuthState.logout,
                            class_name="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors shadow-sm",
                        ),
                        class_name="flex items-center gap-4",
                    ),
                    rx.el.div(
                        rx.el.a(
                            "Login",
                            href="/login",
                            class_name="px-4 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors",
                        ),
                        rx.el.a(
                            "Register",
                            href="/register",
                            class_name="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors shadow-sm",
                        ),
                        class_name="flex items-center gap-2",
                    ),
                )
            ),
            class_name="container mx-auto flex items-center justify-between p-4",
        ),
        class_name="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50",
    )