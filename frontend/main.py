import flet as ft
from mocks import MOCK_USERS, NAV_ITEMS

# Ancho límite: por encima usamos Navigation Rail (escritorio/tablet),
# por debajo usamos Bottom Navigation (Fitts law: botones alcanzables
# con el pulgar en móvil).
BREAKPOINT_DESKTOP = 700


def main(page: ft.Page):
    page.title = "Sistema de Asistencia"
    # Paleta: teal como color primario (transmite orden/confianza,
    # apropiado para un contexto escolar), Material 3.
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.TEAL)
    page.padding = 0

    # Estado simple en memoria (mock de "sesión activa").
    # En FASE 4 esto vendrá de la tabla `sessions` real.
    state = {"role": "admin", "selected_index": 0}

    content_area = ft.Container(expand=True, padding=20)
    nav_rail = ft.NavigationRail(visible=False)
    nav_bar = ft.NavigationBar(visible=False)

    def build_destinations_rail(role: str):
        return [
            ft.NavigationRailDestination(
                icon=getattr(ft.Icons, icon_name),
                label=label,
            )
            for icon_name, label in NAV_ITEMS[role]
        ]

    def build_destinations_bar(role: str):
        return [
            ft.NavigationBarDestination(
                icon=getattr(ft.Icons, icon_name),
                label=label,
            )
            for icon_name, label in NAV_ITEMS[role]
        ]

    def render_content():
        # Estado del sistema visible: mostramos qué rol y qué sección
        # está activa, evitando que el usuario se pierda.
        role = state["role"]
        label = NAV_ITEMS[role][state["selected_index"]][1]
        user = MOCK_USERS[role]
        content_area.content = ft.Column(
            [
                ft.Text(f"Sección: {label}", size=22, weight=ft.FontWeight.W_500),
                ft.Text(f"Usuario: {user['name']} ({role})", color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Divider(),
                ft.Text("Contenido simulado — se conecta a Convex en FASE 4."),
            ]
        )
        page.update()

    def on_rail_change(e):
        state["selected_index"] = e.control.selected_index
        render_content()

    def on_bar_change(e):
        state["selected_index"] = e.control.selected_index
        render_content()

    def apply_layout(width: int):
        # Aquí ocurre la decisión responsiva: un solo layout activo a la vez.
        is_desktop = width >= BREAKPOINT_DESKTOP
        nav_rail.visible = is_desktop
        nav_bar.visible = not is_desktop
        page.update()

    def switch_role(role: str):
        state["role"] = role
        state["selected_index"] = 0
        nav_rail.destinations = build_destinations_rail(role)
        nav_rail.selected_index = 0
        nav_bar.destinations = build_destinations_bar(role)
        nav_bar.selected_index = 0
        render_content()

    # Configuración inicial de los controles de navegación
    nav_rail.destinations = build_destinations_rail(state["role"])
    nav_rail.selected_index = 0
    nav_rail.label_type = ft.NavigationRailLabelType.ALL
    nav_rail.on_change = on_rail_change

    nav_bar.destinations = build_destinations_bar(state["role"])
    nav_bar.selected_index = 0
    nav_bar.on_change = on_bar_change
    page.navigation_bar = nav_bar

    # Selector de rol temporal (simula "login" mientras no hay auth real)
    role_selector = ft.SegmentedButton(
        selected=[state["role"]],
        segments=[
            ft.Segment(value="admin", label=ft.Text("Admin")),
            ft.Segment(value="docente", label=ft.Text("Docente")),
            ft.Segment(value="alumno", label=ft.Text("Alumno")),
        ],
        on_change=lambda e: switch_role(list(e.control.selected)[0]),
    )

    page.add(
        ft.Container(
            content=ft.Row(
                [ft.Text("Vista de prueba — rol:"), role_selector],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=10,
        ),
        ft.Row(
            [nav_rail, ft.VerticalDivider(width=1), content_area],
            expand=True,
        ),
    )

    apply_layout(page.width)
    page.on_resize = lambda e: apply_layout(page.width)
    render_content()


ft.app(target=main)
