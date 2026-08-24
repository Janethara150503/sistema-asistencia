import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const createCycle = mutation({
  args: {
    name: v.string(),
    startDate: v.string(),
    endDate: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("cycles", {
      name: args.name,
      startDate: args.startDate,
      endDate: args.endDate,
      active: true,
    });
  },
});

export const listCycles = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("cycles").collect();
  },
});

export const createGrade = mutation({
  args: {
    name: v.string(),
    cycleId: v.id("cycles"),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("grades", {
      name: args.name,
      cycleId: args.cycleId,
    });
  },
});

export const listGradesByCycle = query({
  args: {
    cycleId: v.id("cycles"),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("grades")
      .withIndex("by_cycle", (q) => q.eq("cycleId", args.cycleId))
      .collect();
  },
});

export const createGroup = mutation({
  args: {
    name: v.string(),
    gradeId: v.id("grades"),
    cycleId: v.id("cycles"),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("groups", {
      name: args.name,
      gradeId: args.gradeId,
      cycleId: args.cycleId,
    });
  },
});

export const listGroupsByGrade = query({
  args: {
    gradeId: v.id("grades"),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("groups")
      .withIndex("by_grade", (q) => q.eq("gradeId", args.gradeId))
      .collect();
  },
});

export const createSubject = mutation({
  args: {
    name: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("subjects", {
      name: args.name,
    });
  },
});

export const listSubjects = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("subjects").collect();
  },
});
