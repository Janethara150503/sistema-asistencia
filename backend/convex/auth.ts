import { v } from "convex/values";
import { mutation } from "./_generated/server";
import bcrypt from "bcryptjs";

// Quita campos sensibles antes de exponer un usuario fuera del servidor.
export function sanitizeUser(user: any) {
  return {
    id: user._id,
    name: user.name,
    email: user.email,
    phone: user.phone,
    role: user.role,
    photoUrl: user.photoUrl,
    theme: user.theme,
  };
}

// Genera un token simple y unico para la sesion.
// No es criptograficamente perfecto, pero es suficiente para MVP.
function generateToken(): string {
  return crypto.randomUUID() + crypto.randomUUID();
}

// --- Funcion auxiliar: crear usuario de prueba ---
// Uso temporal mientras no existe pantalla de registro (FASE 4).
// TODO: remover o proteger esta funcion antes de produccion.
export const createUser = mutation({
  args: {
    name: v.string(),
    email: v.string(),
    phone: v.string(),
    role: v.union(v.literal("admin"), v.literal("docente"), v.literal("alumno")),
    password: v.string(),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", args.email))
      .first();

    if (existing) {
      throw new Error("Ya existe un usuario con ese correo");
    }

    const passwordHash = bcrypt.hashSync(args.password, 10);

    const userId = await ctx.db.insert("users", {
      name: args.name,
      email: args.email,
      phone: args.phone,
      role: args.role,
      passwordHash,
      theme: "light",
    });

    return userId;
  },
});

// --- Login ---
// Verifica credenciales y crea una sesion con token.
export const login = mutation({
  args: {
    email: v.string(),
    password: v.string(),
  },
  handler: async (ctx, args) => {
    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", args.email))
      .first();

    if (!user) {
      throw new Error("Correo o contrasena incorrectos");
    }

    const passwordMatches = bcrypt.compareSync(args.password, user.passwordHash);
    if (!passwordMatches) {
      throw new Error("Correo o contrasena incorrectos");
    }

    const token = generateToken();
    const expiresAt = Date.now() + 1000 * 60 * 60 * 24 * 7; // 7 dias

    await ctx.db.insert("sessions", {
      userId: user._id,
      token,
      expiresAt,
    });

    return {
      token,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        role: user.role,
      },
    };
  },
});

// --- Validar sesion ---
// Dado un token, confirma si es valido y no expiro, y devuelve el usuario.
export const validateSession = mutation({
  args: {
    token: v.string(),
  },
  handler: async (ctx, args) => {
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_token", (q) => q.eq("token", args.token))
      .first();

    if (!session || session.expiresAt < Date.now()) {
      return null;
    }

    const user = await ctx.db.get(session.userId);
    if (!user) return null;

    return {
      id: user._id,
      name: user.name,
      email: user.email,
      role: user.role,
    };
  },
});

// --- Logout ---
export const logout = mutation({
  args: {
    token: v.string(),
  },
  handler: async (ctx, args) => {
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_token", (q) => q.eq("token", args.token))
      .first();

    if (session) {
      await ctx.db.delete(session._id);
    }

    return { success: true };
  },
});
