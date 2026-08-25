import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

const statusValidator = v.union(
  v.literal("presente"),
  v.literal("ausente"),
  v.literal("retardo"),
  v.literal("justificado")
);

export const registerAttendance = mutation({
  args: {
    studentId: v.id("users"),
    groupId: v.id("groups"),
    subjectId: v.id("subjects"),
    teacherId: v.id("users"),
    date: v.string(),
    status: statusValidator,
    notes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("attendanceRecords")
      .withIndex("by_group_date", (q) =>
        q.eq("groupId", args.groupId).eq("date", args.date)
      )
      .filter((q) =>
        q.and(
          q.eq(q.field("studentId"), args.studentId),
          q.eq(q.field("subjectId"), args.subjectId)
        )
      )
      .first();
    if (existing) {
      await ctx.db.patch(existing._id, { status: args.status, notes: args.notes });
      return existing._id;
    }
    return await ctx.db.insert("attendanceRecords", {
      studentId: args.studentId,
      groupId: args.groupId,
      subjectId: args.subjectId,
      teacherId: args.teacherId,
      date: args.date,
      status: args.status,
      notes: args.notes,
    });
  },
});

export const registerBulkAttendance = mutation({
  args: {
    groupId: v.id("groups"),
    subjectId: v.id("subjects"),
    teacherId: v.id("users"),
    date: v.string(),
    records: v.array(
      v.object({
        studentId: v.id("users"),
        status: statusValidator,
      })
    ),
  },
  handler: async (ctx, args) => {
    const results = [];
    for (const record of args.records) {
      const existing = await ctx.db
        .query("attendanceRecords")
        .withIndex("by_group_date", (q) =>
          q.eq("groupId", args.groupId).eq("date", args.date)
        )
        .filter((q) =>
          q.and(
            q.eq(q.field("studentId"), record.studentId),
            q.eq(q.field("subjectId"), args.subjectId)
          )
        )
        .first();
      if (existing) {
        await ctx.db.patch(existing._id, { status: record.status });
        results.push(existing._id);
      } else {
        const id = await ctx.db.insert("attendanceRecords", {
          studentId: record.studentId,
          groupId: args.groupId,
          subjectId: args.subjectId,
          teacherId: args.teacherId,
          date: args.date,
          status: record.status,
        });
        results.push(id);
      }
    }
    return results;
  },
});

export const listAttendanceByGroupDate = query({
  args: {
    groupId: v.id("groups"),
    date: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("attendanceRecords")
      .withIndex("by_group_date", (q) =>
        q.eq("groupId", args.groupId).eq("date", args.date)
      )
      .collect();
  },
});
