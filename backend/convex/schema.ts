import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    name: v.string(),
    email: v.string(),
    phone: v.string(),
    photoUrl: v.optional(v.string()),
    role: v.union(v.literal("admin"), v.literal("docente"), v.literal("alumno")),
    passwordHash: v.string(),
    theme: v.union(v.literal("light"), v.literal("dark")),
  }).index("by_email", ["email"]),

  sessions: defineTable({
    userId: v.id("users"),
    token: v.string(),
    expiresAt: v.number(),
  }).index("by_token", ["token"]),

  cycles: defineTable({
    name: v.string(),
    startDate: v.string(),
    endDate: v.string(),
    active: v.boolean(),
  }),

  grades: defineTable({
    name: v.string(),
    cycleId: v.id("cycles"),
  }).index("by_cycle", ["cycleId"]),

  groups: defineTable({
    name: v.string(),
    gradeId: v.id("grades"),
    cycleId: v.id("cycles"),
  }).index("by_grade", ["gradeId"]),

  subjects: defineTable({
    name: v.string(),
  }),

  teacherAssignments: defineTable({
    teacherId: v.id("users"),
    subjectId: v.id("subjects"),
    groupId: v.id("groups"),
    cycleId: v.id("cycles"),
  }).index("by_teacher", ["teacherId"])
    .index("by_group", ["groupId"]),

  enrollments: defineTable({
    studentId: v.id("users"),
    groupId: v.id("groups"),
    cycleId: v.id("cycles"),
  }).index("by_student", ["studentId"])
    .index("by_group", ["groupId"]),

  attendanceConfig: defineTable({
    cycleId: v.id("cycles"),
    entryTime: v.string(),
    lateLimitTime: v.string(),
    exitTime: v.string(),
    toleranceMinutes: v.number(),
    workDays: v.array(v.number()),
  }).index("by_cycle", ["cycleId"]),

  attendanceRecords: defineTable({
    studentId: v.id("users"),
    groupId: v.id("groups"),
    subjectId: v.id("subjects"),
    teacherId: v.id("users"),
    date: v.string(),
    status: v.union(
      v.literal("presente"),
      v.literal("ausente"),
      v.literal("retardo"),
      v.literal("justificado")
    ),
    notes: v.optional(v.string()),
  }).index("by_student", ["studentId"])
    .index("by_group_date", ["groupId", "date"]),

  notifications: defineTable({
    userId: v.id("users"),
    type: v.union(
      v.literal("asistencia"),
      v.literal("inasistencia"),
      v.literal("recordatorio"),
      v.literal("sistema")
    ),
    channel: v.union(v.literal("in_app"), v.literal("email"), v.literal("sms")),
    message: v.string(),
    read: v.boolean(),
    status: v.union(v.literal("pending"), v.literal("sent"), v.literal("failed")),
  }).index("by_user", ["userId"]),
});
