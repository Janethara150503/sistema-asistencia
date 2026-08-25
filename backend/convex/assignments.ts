import { v } from "convex/values";
import { sanitizeUser } from "./auth";
import { mutation, query } from "./_generated/server";

// ============ INSCRIPCIONES (alumno -> grupo) ============

export const enrollStudent = mutation({
  args: {
    studentId: v.id("users"),
    groupId: v.id("groups"),
    cycleId: v.id("cycles"),
  },
  handler: async (ctx, args) => {
    const student = await ctx.db.get(args.studentId);
    if (!student || student.role !== "alumno") {
      throw new Error("El usuario indicado no es un alumno");
    }

    return await ctx.db.insert("enrollments", {
      studentId: args.studentId,
      groupId: args.groupId,
      cycleId: args.cycleId,
    });
  },
});

export const listStudentsByGroup = query({
  args: {
    groupId: v.id("groups"),
  },
  handler: async (ctx, args) => {
    const enrollments = await ctx.db
      .query("enrollments")
      .withIndex("by_group", (q) => q.eq("groupId", args.groupId))
      .collect();

    const students = await Promise.all(
      enrollments.map((e) => ctx.db.get(e.studentId))
    );

    return students.filter((s) => s !== null).map(sanitizeUser);
  },
});

export const listGroupsByStudent = query({
  args: {
    studentId: v.id("users"),
  },
  handler: async (ctx, args) => {
    const enrollments = await ctx.db
      .query("enrollments")
      .withIndex("by_student", (q) => q.eq("studentId", args.studentId))
      .collect();

    const groups = await Promise.all(
      enrollments.map((e) => ctx.db.get(e.groupId))
    );

    return groups.filter((g) => g !== null);
  },
});

// ============ ASIGNACIONES (docente -> materia -> grupo) ============

export const assignTeacher = mutation({
  args: {
    teacherId: v.id("users"),
    subjectId: v.id("subjects"),
    groupId: v.id("groups"),
    cycleId: v.id("cycles"),
  },
  handler: async (ctx, args) => {
    const teacher = await ctx.db.get(args.teacherId);
    if (!teacher || teacher.role !== "docente") {
      throw new Error("El usuario indicado no es un docente");
    }

    return await ctx.db.insert("teacherAssignments", {
      teacherId: args.teacherId,
      subjectId: args.subjectId,
      groupId: args.groupId,
      cycleId: args.cycleId,
    });
  },
});

export const listAssignmentsByTeacher = query({
  args: {
    teacherId: v.id("users"),
  },
  handler: async (ctx, args) => {
    const assignments = await ctx.db
      .query("teacherAssignments")
      .withIndex("by_teacher", (q) => q.eq("teacherId", args.teacherId))
      .collect();

    return await Promise.all(
      assignments.map(async (a) => ({
        ...a,
        group: await ctx.db.get(a.groupId),
        subject: await ctx.db.get(a.subjectId),
      }))
    );
  },
});

export const listAssignmentsByGroup = query({
  args: {
    groupId: v.id("groups"),
  },
  handler: async (ctx, args) => {
    const assignments = await ctx.db
      .query("teacherAssignments")
      .withIndex("by_group", (q) => q.eq("groupId", args.groupId))
      .collect();

    return await Promise.all(
      assignments.map(async (a) => ({
        ...a,
        teacher: await ctx.db.get(a.teacherId).then((t) => (t ? sanitizeUser(t) : null)),
        subject: await ctx.db.get(a.subjectId),
      }))
    );
  },
});
