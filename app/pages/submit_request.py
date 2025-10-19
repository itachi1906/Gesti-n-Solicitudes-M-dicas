import reflex as rx
from app.state import RequestState, AuthState, protected_page
from app.components.navbar import navbar


def form_field(
    label: str,
    name: str,
    placeholder: str,
    type: str = "text",
    is_textarea: bool = False,
) -> rx.Component:
    Component = rx.el.textarea if is_textarea else rx.el.input
    return rx.el.div(
        rx.el.label(label, class_name="text-sm font-medium text-gray-700 mb-2 block"),
        Component(
            name=name,
            type=type,
            placeholder=placeholder,
            class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow",
            rows=5 if is_textarea else None,
        ),
        class_name="w-full",
    )


def submit_request_form() -> rx.Component:
    return rx.el.form(
        rx.el.div(
            rx.el.h1(
                "New Medical Request", class_name="text-3xl font-bold text-gray-800"
            ),
            rx.el.p(
                "Fill out the details below to submit your request.",
                class_name="text-gray-500 mt-2 mb-8",
            ),
            rx.el.div(
                rx.el.h2(
                    "Patient Information",
                    class_name="text-xl font-semibold text-gray-700 border-b pb-2 mb-6",
                ),
                rx.el.div(
                    form_field("Full Name", "patient_name", "John Doe"),
                    form_field("Age", "patient_age", "35", type="number"),
                    class_name="grid md:grid-cols-2 gap-6 mb-6",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Gender",
                            class_name="text-sm font-medium text-gray-700 mb-2 block",
                        ),
                        rx.el.select(
                            rx.el.option("Male", value="male"),
                            rx.el.option("Female", value="female"),
                            rx.el.option("Other", value="other"),
                            name="patient_gender",
                            class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow appearance-none bg-white",
                        ),
                        class_name="w-full",
                    ),
                    form_field("ID Number", "patient_id_number", "123456789"),
                    class_name="grid md:grid-cols-2 gap-6 mb-6",
                ),
                class_name="mb-10",
            ),
            rx.el.div(
                rx.el.h2(
                    "Medical Details",
                    class_name="text-xl font-semibold text-gray-700 border-b pb-2 mb-6",
                ),
                rx.el.div(
                    form_field(
                        "Symptoms",
                        "symptoms",
                        "Describe the patient's symptoms...",
                        is_textarea=True,
                    ),
                    form_field(
                        "Provisional Diagnosis (Optional)",
                        "diagnosis",
                        "e.g., Common Cold",
                        is_textarea=True,
                    ),
                    class_name="grid md:grid-cols-1 gap-6 mb-6",
                ),
                rx.el.div(
                    form_field(
                        "Current Medications (Optional)",
                        "medications",
                        "e.g., Paracetamol 500mg",
                        is_textarea=True,
                    ),
                    form_field(
                        "Medical History (Optional)",
                        "medical_history",
                        "e.g., Asthma, Diabetes",
                        is_textarea=True,
                    ),
                    class_name="grid md:grid-cols-1 gap-6 mb-6",
                ),
                class_name="mb-10",
            ),
            rx.el.div(
                rx.el.h2(
                    "Supporting Documents",
                    class_name="text-xl font-semibold text-gray-700 border-b pb-2 mb-6",
                ),
                rx.upload.root(
                    rx.el.div(
                        rx.icon(
                            tag="cloud_upload",
                            class_name="w-10 h-10 mx-auto text-gray-400",
                        ),
                        rx.el.p("Drag & drop files here, or click to select files"),
                        class_name="text-center p-8 border-2 border-dashed border-gray-300 rounded-lg hover:bg-gray-50 cursor-pointer",
                    ),
                    id="upload_area",
                    multiple=True,
                    accept={
                        "application/pdf": [".pdf"],
                        "image/jpeg": [".jpg", ".jpeg"],
                        "image/png": [".png"],
                    },
                    max_files=5,
                    on_drop=RequestState.handle_upload(
                        rx.upload_files(upload_id="upload_area")
                    ),
                    class_name="w-full",
                ),
                rx.el.div(
                    rx.foreach(
                        RequestState.uploaded_documents,
                        lambda doc: rx.el.div(
                            rx.icon(tag="file-text", class_name="w-4 h-4 mr-2"),
                            rx.el.span(doc),
                            class_name="flex items-center text-sm p-2 bg-gray-100 border border-gray-200 rounded-md",
                        ),
                    ),
                    class_name="mt-4 grid grid-cols-2 md:grid-cols-3 gap-2",
                ),
                class_name="mb-10",
            ),
            rx.el.button(
                rx.cond(
                    RequestState.is_submitting,
                    rx.spinner(class_name="w-5 h-5"),
                    "Submit Medical Request",
                ),
                type="submit",
                class_name="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition-colors shadow-md flex items-center justify-center disabled:opacity-50",
                disabled=RequestState.is_submitting,
            ),
            class_name="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-2xl shadow-lg border border-gray-100 my-12",
        ),
        on_submit=RequestState.submit_request,
    )


def submit_request_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(protected_page(submit_request_form()), class_name="bg-gray-50"),
        class_name="font-['JetBrains_Mono'] min-h-screen",
    )