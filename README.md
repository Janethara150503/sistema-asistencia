# Sistema de Asistencia Digital

MVP multiplataforma (Windows/Android) para gestión de asistencia escolar.
Roles: Administrador, Docente, Alumno.

Stack: Flet (frontend) + Convex (backend/DB) + Railway (deploy) + Cloudflare (DNS/seguridad).

## Estado
FASE 0 — PRD en definición.

## Decisiones de arquitectura (FASE 1)
- Auth: sesión con token propio (no Convex Auth, por incompatibilidad con cliente Python/Flet).
- Notificaciones MVP: in-app + email (Resend). SMS (Twilio) = backlog post-MVP.
- Railway: exclusivo para generación de reportes PDF/Excel (FastAPI). Todo lo demás vive en Convex.
