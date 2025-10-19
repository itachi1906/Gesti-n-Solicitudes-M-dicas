import reflex as rx
from app.state import AuthState
from app.components.navbar import navbar


def login_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "Sign In",
                        class_name="text-3xl font-bold text-gray-800 text-center",
                    ),
                    rx.el.p(
                        "Access your medical request dashboard.",
                        class_name="text-center text-gray-500 mt-2 mb-8",
                    ),
                    rx.cond(
                        AuthState.error_message != "",
                        rx.el.div(
                            AuthState.error_message,
                            class_name="w-full p-3 mb-4 text-sm text-red-700 bg-red-100 border border-red-200 rounded-lg text-center",
                        ),
                        rx.fragment(),
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.label(
                                "Email Address",
                                class_name="text-sm font-medium text-gray-700 mb-2 block",
                            ),
                            rx.el.input(
                                type="email",
                                name="email",
                                placeholder="you@example.com",
                                class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow",
                                on_focus=AuthState.clear_error,
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Password",
                                class_name="text-sm font-medium text-gray-700 mb-2 block",
                            ),
                            rx.el.input(
                                type="password",
                                name="password",
                                placeholder="••••••••",
                                class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow",
                                on_focus=AuthState.clear_error,
                            ),
                            class_name="mb-6",
                        ),
                        rx.el.button(
                            rx.cond(
                                AuthState.is_loading,
                                rx.spinner(class_name="w-5 h-5"),
                                "Sign In",
                            ),
                            type="submit",
                            class_name="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition-colors shadow-md flex items-center justify-center disabled:opacity-50",
                            disabled=AuthState.is_loading,
                        ),
                        on_submit=AuthState.login,
                    ),
                    rx.el.p(
                        "Don't have an account? ",
                        rx.el.a(
                            "Register here",
                            href="/register",
                            class_name="font-semibold text-blue-600 hover:underline",
                        ),
                        class_name="text-center text-sm text-gray-600 mt-8",
                    ),
                    class_name="w-full max-w-md bg-white p-8 md:p-12 rounded-2xl shadow-lg border border-gray-100",
                ),
                class_name="min-h-[80vh] flex flex-col items-center justify-center p-4",
            )
        ),
        class_name="font-['JetBrains_Mono'] bg-gray-50 min-h-screen",
    )