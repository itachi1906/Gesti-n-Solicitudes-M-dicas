import reflex as rx
from typing import Optional, TypedDict
from sqlmodel import select
import bcrypt
import datetime
from .models import (
    User,
    UserRole,
    RequestStatus,
    SQLModelUser,
    MedicalRequest as SQLModelMedicalRequest,
)


class FormValidationError(TypedDict):
    field: str
    message: str


class RequestState(rx.State):
    is_submitting: bool = False
    form_errors: list[FormValidationError] = []
    uploaded_documents: list[str] = []

    def _validate_form(self, form_data: dict) -> bool:
        self.form_errors = []
        required_fields = [
            "patient_name",
            "patient_age",
            "patient_id_number",
            "symptoms",
        ]
        for field in required_fields:
            if not form_data.get(field, "").strip():
                self.form_errors.append(
                    FormValidationError(
                        field=field,
                        message=f"{field.replace('_', ' ').title()} is required.",
                    )
                )
        age_str = form_data.get("patient_age", "0")
        if not age_str.isdigit() or not 0 < int(age_str) <= 120:
            self.form_errors.append(
                FormValidationError(
                    field="patient_age",
                    message="Please enter a valid age between 1 and 120.",
                )
            )
        return len(self.form_errors) == 0

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            yield rx.toast.error("No files selected.")
            return
        for file in files:
            upload_data = await file.read()
            unique_name = (
                f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}_{file.name}"
            )
            path = rx.get_upload_dir() / unique_name
            with path.open("wb") as f:
                f.write(upload_data)
            self.uploaded_documents.append(unique_name)
        yield rx.toast.success(f"Successfully uploaded {len(files)} files.")

    @rx.event
    async def submit_request(self, form_data: dict):
        self.is_submitting = True
        yield
        if not self._validate_form(form_data):
            self.is_submitting = False
            for error in self.form_errors:
                yield rx.toast.error(error["message"])
            return
        auth_state = await self.get_state(AuthState)
        if not auth_state.current_user:
            self.is_submitting = False
            yield rx.toast.error("You must be logged in to submit a request.")
            yield rx.redirect("/login")
            return
        new_request = SQLModelMedicalRequest(
            patient_name=form_data["patient_name"],
            patient_age=int(form_data["patient_age"]),
            patient_gender=form_data["patient_gender"],
            patient_id_number=form_data["patient_id_number"],
            symptoms=form_data["symptoms"],
            diagnosis=form_data.get("diagnosis", ""),
            medications=form_data.get("medications", ""),
            medical_history=form_data.get("medical_history", ""),
            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            status=RequestStatus.PENDING.value,
            user_id=auth_state.current_user["id"],
            documents=",".join(self.uploaded_documents),
        )
        async with rx.asession("sqlite+aiosqlite:///reflex.db") as session:
            session.add(new_request)
            await session.commit()
        self.is_submitting = False
        self.uploaded_documents = []
        yield rx.toast.success("Medical request submitted successfully!")
        yield rx.redirect("/")
        return


class AuthState(rx.State):
    user_id: rx.LocalStorage = ""
    is_authenticated: bool = False
    current_user: Optional[User] = None
    error_message: str = ""
    is_loading: bool = False

    @rx.var
    def is_manager(self) -> bool:
        return (
            self.current_user is not None
            and self.current_user["role"] == UserRole.MANAGER.value
        )

    async def _check_session(self):
        if self.user_id:
            async with rx.asession("sqlite+aiosqlite:///reflex.db") as session:
                result = await session.exec(
                    select(SQLModelUser).where(SQLModelUser.id == self.user_id)
                )
                user_db = result.one_or_none()
                if user_db:
                    self.current_user = User(
                        id=user_db.id,
                        email=user_db.email,
                        password_hash=user_db.password_hash,
                        role=UserRole(user_db.role).value,
                    )
                    self.is_authenticated = True
                else:
                    self.is_authenticated = False
                    self.current_user = None
                    self.user_id = ""

    @rx.event
    async def on_load(self):
        await self._check_session()

    @rx.event
    async def register(self, form_data: dict):
        self.is_loading = True
        yield
        email = form_data.get("email", "").lower()
        password = form_data.get("password", "")
        role_str = form_data.get("role", "common_user")
        if not email or not password:
            self.error_message = "Email and password are required."
            self.is_loading = False
            return
        async with rx.asession("sqlite+aiosqlite:///reflex.db") as session:
            existing_user_result = await session.exec(
                select(SQLModelUser).where(SQLModelUser.email == email)
            )
            if existing_user_result.one_or_none():
                self.error_message = "An account with this email already exists."
                self.is_loading = False
                return
            role = UserRole(role_str)
            if role == UserRole.MANAGER:
                existing_manager_result = await session.exec(
                    select(SQLModelUser).where(
                        SQLModelUser.role == UserRole.MANAGER.value
                    )
                )
                if existing_manager_result.one_or_none():
                    self.error_message = (
                        "A manager account already exists. Only one is allowed."
                    )
                    self.is_loading = False
                    return
            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            new_user_db = SQLModelUser(
                email=email, password_hash=hashed_password, role=role.value
            )
            session.add(new_user_db)
            await session.commit()
            await session.refresh(new_user_db)
            if new_user_db.id:
                new_user: User = User(
                    id=new_user_db.id,
                    email=new_user_db.email,
                    password_hash=new_user_db.password_hash,
                    role=UserRole(new_user_db.role).value,
                )
                self.user_id = str(new_user["id"])
                self.current_user = new_user
                self.is_authenticated = True
                self.error_message = ""
                self.is_loading = False
                yield rx.redirect("/")
                return

    @rx.event
    async def login(self, form_data: dict):
        self.is_loading = True
        yield
        email = form_data.get("email", "").lower()
        password = form_data.get("password", "")
        if not email or not password:
            self.error_message = "Email and password are required."
            self.is_loading = False
            return
        async with rx.asession("sqlite+aiosqlite:///reflex.db") as session:
            result = await session.exec(
                select(SQLModelUser).where(SQLModelUser.email == email)
            )
            user_db = result.one_or_none()
            if user_db and bcrypt.checkpw(
                password.encode("utf-8"), user_db.password_hash.encode("utf-8")
            ):
                user: User = User(
                    id=user_db.id,
                    email=user_db.email,
                    password_hash=user_db.password_hash,
                    role=UserRole(user_db.role).value,
                )
                self.user_id = str(user["id"])
                self.current_user = user
                self.is_authenticated = True
                self.error_message = ""
                self.is_loading = False
                yield rx.redirect("/")
                return
            else:
                self.error_message = "Invalid email or password."
                self.is_loading = False
                return

    @rx.event
    def logout(self):
        self.user_id = ""
        self.is_authenticated = False
        self.current_user = None
        return rx.redirect("/login")

    @rx.event
    def clear_error(self):
        self.error_message = ""


def protected_page(page_content: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_authenticated,
            page_content,
            rx.el.div(
                rx.spinner(class_name="text-blue-500 w-12 h-12"),
                class_name="flex items-center justify-center min-h-screen",
            ),
        ),
        on_mount=AuthState.on_load,
    )