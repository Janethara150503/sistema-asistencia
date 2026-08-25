import { v } from "convex/values";
import { action, internalMutation, internalQuery } from "./_generated/server";
import { internal } from "./_generated/api";
import { Resend } from "resend";

// Query interna: solo la puede llamar otra funcion de Convex, no el cliente.
// La usamos desde la action para leer datos del alumno.
export const getStudentForNotification = internalQuery({
  args: { studentId: v.id("users") },
  handler: async (ctx, args) => {
    const student = await ctx.db.get(args.studentId);
    if (!student) return null;
    return { name: student.name, email: student.email };
  },
});

// Mutation interna: guarda el registro de la notificacion en la tabla.
export const logNotification = internalMutation({
  args: {
    userId: v.id("users"),
    message: v.string(),
    status: v.union(v.literal("sent"), v.literal("failed")),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("notifications", {
      userId: args.userId,
      type: "inasistencia",
      channel: "email",
      message: args.message,
      read: false,
      status: args.status,
    });
  },
});

// Action: envia el correo de aviso de inasistencia y registra el resultado.
// Se llama desde el cliente Flet (o luego, automaticamente, desde
// registerAttendance) cuando un alumno se marca como "ausente".
export const sendAbsenceNotification = action({
  args: {
    studentId: v.id("users"),
    date: v.string(),
  },
  handler: async (ctx, args) => {
    const student = await ctx.runQuery(
      internal.notifications.getStudentForNotification,
      { studentId: args.studentId }
    );

    if (!student) {
      throw new Error("Alumno no encontrado");
    }

    const message = `El alumno ${student.name} falto el dia ${args.date}.`;
    const resend = new Resend(process.env.RESEND_API_KEY);

    try {
      await resend.emails.send({
        from: "onboarding@resend.dev",
        to: student.email,
        subject: "Aviso de inasistencia",
        text: message,
      });

      await ctx.runMutation(internal.notifications.logNotification, {
        userId: args.studentId,
        message,
        status: "sent",
      });

      return { success: true };
    } catch (error) {
      await ctx.runMutation(internal.notifications.logNotification, {
        userId: args.studentId,
        message,
        status: "failed",
      });

      return { success: false, error: String(error) };
    }
  },
});
