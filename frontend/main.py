import flet as ft
from convex_client import client
from mocks import NAV_ITEMS

BREAKPOINT_DESKTOP = 700


async def main(page: ft.Page):
    page.title = "Sistema de Asistencia"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.TEAL)
    page.padding = 0
    page.bgcolor = ft.Colors.WHITE

    session = {"token": None, "user": None}

    email_field = ft.TextField(
        label="Correo electronico",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        width=320,
        border_radius=8,
    )
    password_field = ft.TextField(
        label="Contrasena",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        width=320,
        border_radius=8,
    )
    login_button = ft.ElevatedButton(
        content=ft.Text("Iniciar sesion", size=16),
        width=320,
        height=48,
        bgcolor=ft.Colors.TEAL,
        color=ft.Colors.WHITE,
    )
    login_spinner = ft.ProgressRing(width=16, height=16, stroke_width=2, visible=False)

    def show_error(message: str):
        page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=ft.Colors.ERROR)
        page.snack_bar.open = True
        page.update()

    def set_loading(is_loading: bool):
        login_button.disabled = is_loading
        login_spinner.visible = is_loading
        page.update()

    async def do_login(e):
        email = email_field.value.strip()
        password = password_field.value
        if not email or not password:
            show_error("Ingresa correo y contrasena")
            return
        set_loading(True)
        try:
            result = client.mutation(
                "auth:login", {"email": email, "password": password}
            )
            session["token"] = result["token"]
            session["user"] = result["user"]
            await page.shared_preferences.set("token", result["token"])
            build_app_view()
        except Exception:
            show_error("Correo o contrasena incorrectos")
        finally:
            set_loading(False)

    login_button.on_click = do_login

    form_column = ft.Column(
        [
            ft.Text("Bienvenido", size=28, weight=ft.FontWeight.W_700),
            ft.Text("Inicia sesion en tu cuenta", color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Container(height=24),
            email_field,
            ft.Container(height=8),
            password_field,
            ft.Container(height=16),
            ft.Row([login_button, login_spinner], alignment=ft.MainAxisAlignment.START),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.START,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    brand_panel = ft.Container(
        content=ft.Column(
            [
                ft.Text("Sistema de Asistencia", size=26, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                ft.Container(height=16),
                ft.Text(
                    "Gestion digital de asistencia escolar para administradores, docentes y alumnos.",
                    color=ft.Colors.WHITE70,
                    size=14,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.TEAL,
        padding=40,
        expand=1,
    )

    form_panel = ft.Container(
        content=form_column,
        padding=40,
        alignment=ft.alignment.Alignment(0, 0),
        expand=1,
    )

    login_view_desktop = ft.Row([brand_panel, form_panel], expand=True)
    login_view_mobile = ft.Container(content=form_panel, expand=True)

    content_area = ft.Container(expand=True, padding=20)
    nav_rail = ft.NavigationRail(visible=False)
    nav_bar = ft.NavigationBar(visible=False)
    app_state = {"selected_index": 0}

    def build_destinations_rail(role):
        return [
            ft.NavigationRailDestination(icon=getattr(ft.Icons, icon), label=label)
            for icon, label in NAV_ITEMS[role]
        ]

    def build_destinations_bar(role):
        return [
            ft.NavigationBarDestination(icon=getattr(ft.Icons, icon), label=label)
            for icon, label in NAV_ITEMS[role]
        ]

    async def do_logout(e):
        if session["token"]:
            try:
                client.mutation("auth:logout", {"token": session["token"]})
            except Exception:
                pass
        await page.shared_preferences.remove("token")
        session["token"] = None
        session["user"] = None
        show_login_view(page.width)

    academic_state = {"entity": "Ciclos"}
    cycles_list_view = ft.Column(spacing=8)

    def refresh_cycles():
        cycles = client.query("academic:listCycles")
        cycles_list_view.controls = [
            ft.Text(f"{c['name']} ({c['startDate']} a {c['endDate']})")
            for c in cycles
        ]
        page.update()

    cycle_name_field = ft.TextField(label="Nombre (ej. 2026-2027)", width=280)
    cycle_start_field = ft.TextField(label="Fecha de inicio (YYYY-MM-DD)", width=280)
    cycle_end_field = ft.TextField(label="Fecha de fin (YYYY-MM-DD)", width=280)

    def close_dialog(e):
        page.pop_dialog()

    def create_cycle(e):
        name = cycle_name_field.value.strip()
        start = cycle_start_field.value.strip()
        end = cycle_end_field.value.strip()
        if not name or not start or not end:
            show_error("Completa todos los campos")
            return
        client.mutation(
            "academic:createCycle",
            {"name": name, "startDate": start, "endDate": end},
        )
        cycle_name_field.value = ""
        cycle_start_field.value = ""
        cycle_end_field.value = ""
        page.pop_dialog()
        refresh_cycles()

    def open_create_cycle_dialog(e):
        cycle_name_field.value = ""
        cycle_start_field.value = ""
        cycle_end_field.value = ""
        dialog = ft.AlertDialog(
            title=ft.Text("Nuevo ciclo escolar"),
            content=ft.Column(
                [cycle_name_field, cycle_start_field, cycle_end_field],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=close_dialog),
                ft.TextButton(content=ft.Text("Crear"), on_click=create_cycle),
            ],
        )
        page.show_dialog(dialog)

    entity_dropdown = ft.Dropdown(
        label="Entidad",
        value="Ciclos",
        width=280,
        options=[
            ft.DropdownOption(key="Ciclos", text="Ciclos escolares"),
            ft.DropdownOption(key="Grados", text="Grados"),
            ft.DropdownOption(key="Grupos", text="Grupos"),
            ft.DropdownOption(key="Materias", text="Materias"),
        ],
    )

    def on_entity_select(e):
        academic_state["entity"] = entity_dropdown.value
        render_academic_view()

    entity_dropdown.on_select = on_entity_select

    def render_academic_view():
        refresh_cycles()
        if academic_state["entity"] == "Materias":
            refresh_subjects()
            section_title = "Materias"
            section_add = open_create_subject_dialog
            section_list = subjects_list_view
        elif academic_state["entity"] == "Grupos":
            refresh_groups()
            section_title = "Grupos"
            section_add = open_create_group_dialog
            section_list = groups_list_view
        elif academic_state["entity"] == "Grados":
            refresh_grades()
            section_title = "Grados"
            section_add = open_create_grade_dialog
            section_list = grades_list_view
        else:
            section_title = "Ciclos escolares"
            section_add = open_create_cycle_dialog
            section_list = cycles_list_view
        content_area.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Configuracion academica", size=22, weight=ft.FontWeight.W_500),
                        ft.TextButton(
                            content=ft.Text("Cerrar sesion"),
                            icon=ft.Icons.LOGOUT,
                            on_click=do_logout,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                entity_dropdown,
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.Text(section_title, weight=ft.FontWeight.W_500),
                        ft.IconButton(icon=ft.Icons.ADD, on_click=section_add),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                section_list,
            ]
        )
        page.update()
    grades_list_view = ft.Column(spacing=8)
    grade_cycle_dropdown = ft.Dropdown(label="Ciclo escolar", width=280, options=[])
    grade_name_field = ft.TextField(label="Nombre (ej. 1er grado)", width=280)

    def refresh_grades():
        cycles = client.query("academic:listCycles")
        grade_cycle_dropdown.options = [
            ft.DropdownOption(key=c["_id"], text=c["name"]) for c in cycles
        ]
        if cycles and not grade_cycle_dropdown.value:
            grade_cycle_dropdown.value = cycles[0]["_id"]

        if grade_cycle_dropdown.value:
            grades = client.query(
                "academic:listGradesByCycle", {"cycleId": grade_cycle_dropdown.value}
            )
            grades_list_view.controls = [ft.Text(g["name"]) for g in grades]
        else:
            grades_list_view.controls = [ft.Text("No hay ciclos escolares creados aun")]
        page.update()

    def create_grade(e):
        name = grade_name_field.value.strip()
        if not name or not grade_cycle_dropdown.value:
            show_error("Completa el nombre y elige un ciclo")
            return
        client.mutation(
            "academic:createGrade",
            {"name": name, "cycleId": grade_cycle_dropdown.value},
        )
        grade_name_field.value = ""
        page.pop_dialog()
        refresh_grades()

    def open_create_grade_dialog(e):
        grade_name_field.value = ""
        dialog = ft.AlertDialog(
            title=ft.Text("Nuevo grado"),
            content=ft.Column(
                [grade_cycle_dropdown, grade_name_field], tight=True, spacing=10
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=close_dialog),
                ft.TextButton(content=ft.Text("Crear"), on_click=create_grade),
            ],
        )
        page.show_dialog(dialog)
    groups_list_view = ft.Column(spacing=8)
    group_grade_dropdown = ft.Dropdown(label="Grado", width=280, options=[])
    group_name_field = ft.TextField(label="Nombre (ej. Grupo A)", width=280)

    def refresh_groups():
        cycles = client.query("academic:listCycles")
        if not cycles:
            groups_list_view.controls = [ft.Text("No hay ciclos escolares creados aun")]
            page.update()
            return

        cycle_id = cycles[0]["_id"]
        grades = client.query("academic:listGradesByCycle", {"cycleId": cycle_id})
        group_grade_dropdown.options = [
            ft.DropdownOption(key=g["_id"], text=g["name"]) for g in grades
        ]
        if grades and not group_grade_dropdown.value:
            group_grade_dropdown.value = grades[0]["_id"]

        if group_grade_dropdown.value:
            groups = client.query(
                "academic:listGroupsByGrade", {"gradeId": group_grade_dropdown.value}
            )
            groups_list_view.controls = [ft.Text(g["name"]) for g in groups]
        else:
            groups_list_view.controls = [ft.Text("No hay grados creados aun")]
        page.update()

    def create_group(e):
        name = group_name_field.value.strip()
        if not name or not group_grade_dropdown.value:
            show_error("Completa el nombre y elige un grado")
            return
        cycles = client.query("academic:listCycles")
        client.mutation(
            "academic:createGroup",
            {
                "name": name,
                "gradeId": group_grade_dropdown.value,
                "cycleId": cycles[0]["_id"],
            },
        )
        group_name_field.value = ""
        page.pop_dialog()
        refresh_groups()

    def open_create_group_dialog(e):
        group_name_field.value = ""
        dialog = ft.AlertDialog(
            title=ft.Text("Nuevo grupo"),
            content=ft.Column(
                [group_grade_dropdown, group_name_field], tight=True, spacing=10
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=close_dialog),
                ft.TextButton(content=ft.Text("Crear"), on_click=create_group),
            ],
        )
        page.show_dialog(dialog)
    subjects_list_view = ft.Column(spacing=8)
    subject_name_field = ft.TextField(label="Nombre (ej. Historia)", width=280)

    def refresh_subjects():
        subjects = client.query("academic:listSubjects")
        subjects_list_view.controls = [ft.Text(s["name"]) for s in subjects]
        page.update()

    def create_subject(e):
        name = subject_name_field.value.strip()
        if not name:
            show_error("Ingresa el nombre de la materia")
            return
        client.mutation("academic:createSubject", {"name": name})
        subject_name_field.value = ""
        page.pop_dialog()
        refresh_subjects()

    def open_create_subject_dialog(e):
        subject_name_field.value = ""
        dialog = ft.AlertDialog(
            title=ft.Text("Nueva materia"),
            content=ft.Column([subject_name_field], tight=True, spacing=10),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=close_dialog),
                ft.TextButton(content=ft.Text("Crear"), on_click=create_subject),
            ],
        )
        page.show_dialog(dialog)
    def render_content():
        role = session["user"]["role"]
        label = NAV_ITEMS[role][app_state["selected_index"]][1]
        content_area.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(f"Seccion: {label}", size=22, weight=ft.FontWeight.W_500),
                        ft.TextButton(
                            content=ft.Text("Cerrar sesion"),
                            icon=ft.Icons.LOGOUT,
                            on_click=do_logout,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    f"Usuario: {session['user']['name']} ({role})",
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Divider(),
                ft.Text("Conectado a Convex real."),
            ]
        )
        page.update()

    def on_nav_change(e):
        app_state["selected_index"] = e.control.selected_index
        render_academic_view() if session["user"]["role"] == "admin" else render_content()

    def show_login_view(width):
        page.controls.clear()
        if width >= BREAKPOINT_DESKTOP:
            page.add(login_view_desktop)
        else:
            page.add(login_view_mobile)
        page.on_resize = lambda e: show_login_view(page.width)
        page.update()

    def apply_layout(width):
        is_desktop = width >= BREAKPOINT_DESKTOP
        nav_rail.visible = is_desktop
        nav_bar.visible = not is_desktop
        page.update()

    def build_app_view():
        role = session["user"]["role"]
        nav_rail.destinations = build_destinations_rail(role)
        nav_rail.selected_index = 0
        nav_rail.label_type = ft.NavigationRailLabelType.ALL
        nav_rail.on_change = on_nav_change

        nav_bar.destinations = build_destinations_bar(role)
        nav_bar.selected_index = 0
        nav_bar.on_change = on_nav_change
        page.navigation_bar = nav_bar

        page.controls.clear()
        page.add(
            ft.Row([nav_rail, ft.VerticalDivider(width=1), content_area], expand=True)
        )
        apply_layout(page.width)
        page.on_resize = lambda e: apply_layout(page.width)
        render_academic_view() if session["user"]["role"] == "admin" else render_content()

    # Al arrancar: si hay un token guardado, validarlo contra Convex.
    # Si sigue vigente, saltar directo a la app; si no, mostrar login.
    saved_token = await page.shared_preferences.get("token")
    if saved_token:
        try:
            user = client.mutation("auth:validateSession", {"token": saved_token})
            if user:
                session["token"] = saved_token
                session["user"] = user
                build_app_view()
            else:
                await page.shared_preferences.remove("token")
                show_login_view(page.width)
        except Exception:
            show_login_view(page.width)
    else:
        show_login_view(page.width)


ft.app(target=main)
