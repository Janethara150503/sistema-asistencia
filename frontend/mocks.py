"""
Datos simulados para FASE 2 (UI sin backend real).
En FASE 4 esto se reemplaza por queries reales a Convex.
"""

# Usuarios de prueba, uno por rol
MOCK_USERS = {
    "admin": {"name": "Ana Administradora", "email": "admin@escuela.mx"},
    "docente": {"name": "Carlos Docente", "email": "docente@escuela.mx"},
    "alumno": {"name": "Sofía Alumna", "email": "alumno@escuela.mx"},
}

# Menú de navegación por rol: (icono, etiqueta)
# El orden importa: los items mas usados van primero (carga cognitiva)
NAV_ITEMS = {
    "admin": [
        ("HOME_OUTLINED", "Resumen"),
        ("PEOPLE_OUTLINE", "Usuarios"),
        ("GROUPS_OUTLINED", "Grupos"),
        ("CHECKLIST_OUTLINED", "Asistencia"),
        ("BAR_CHART_OUTLINED", "Reportes"),
        ("SETTINGS_OUTLINED", "Ajustes"),
    ],
    "docente": [
        ("GROUPS_OUTLINED", "Mis grupos"),
        ("CHECK_CIRCLE_OUTLINE", "Registrar"),
        ("BAR_CHART_OUTLINED", "Estadísticas"),
        ("SCHEDULE_OUTLINED", "Horarios"),
        ("SETTINGS_OUTLINED", "Ajustes"),
    ],
    "alumno": [
        ("EVENT_AVAILABLE_OUTLINED", "Mi asistencia"),
        ("PIE_CHART_OUTLINE", "Mi %"),
        ("HISTORY_OUTLINED", "Historial"),
        ("NOTIFICATIONS_OUTLINED", "Notificaciones"),
        ("SETTINGS_OUTLINED", "Ajustes"),
    ],
}
