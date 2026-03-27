import { Router, type IRouter } from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { db, usersTable, candidateProfilesTable } from "@workspace/db";
import { eq } from "drizzle-orm";

const router: IRouter = Router();

const JWT_SECRET = process.env.JWT_SECRET_KEY || "trampo-super-secret-key-2026";

function signToken(userId: number) {
  return jwt.sign({ userId }, JWT_SECRET, { expiresIn: "7d" });
}

export function verifyToken(token: string): { userId: number } {
  return jwt.verify(token, JWT_SECRET) as { userId: number };
}

router.post("/register", async (req, res) => {
  const { name, email, password, role, phone, cidade, estado } = req.body;
  if (!name || !email || !password || !role) {
    return res.status(400).json({ error: "Campos obrigatórios faltando" });
  }
  if (!["candidate", "recruiter"].includes(role)) {
    return res.status(400).json({ error: "Role inválida" });
  }
  const existing = await db.select().from(usersTable).where(eq(usersTable.email, email)).limit(1);
  if (existing.length > 0) {
    return res.status(400).json({ error: "Email já cadastrado" });
  }
  const password_hash = await bcrypt.hash(password, 10);
  const [user] = await db.insert(usersTable).values({
    name, email, password_hash, role, phone, cidade, estado
  }).returning();
  if (role === "candidate") {
    await db.insert(candidateProfilesTable).values({ user_id: user.id }).onConflictDoNothing();
  }
  const token = signToken(user.id);
  const { password_hash: _, ...userSafe } = user;
  return res.status(201).json({ token, user: userSafe });
});

router.post("/login", async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ error: "Email e senha obrigatórios" });
  }
  const [user] = await db.select().from(usersTable).where(eq(usersTable.email, email)).limit(1);
  if (!user) {
    return res.status(401).json({ error: "Credenciais inválidas" });
  }
  const valid = await bcrypt.compare(password, user.password_hash);
  if (!valid) {
    return res.status(401).json({ error: "Credenciais inválidas" });
  }
  const token = signToken(user.id);
  const { password_hash: _, ...userSafe } = user;
  return res.json({ token, user: userSafe });
});

router.get("/me", async (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith("Bearer ")) {
    return res.status(401).json({ error: "Token não fornecido" });
  }
  const token = authHeader.slice(7);
  try {
    const { userId } = verifyToken(token);
    const [user] = await db.select().from(usersTable).where(eq(usersTable.id, userId)).limit(1);
    if (!user) return res.status(404).json({ error: "Usuário não encontrado" });
    const { password_hash: _, ...userSafe } = user;
    return res.json(userSafe);
  } catch {
    return res.status(401).json({ error: "Token inválido" });
  }
});

router.post("/forgot-password", async (req, res) => {
  const { email } = req.body;
  if (!email) return res.status(400).json({ error: "Email obrigatório" });
  const [user] = await db.select().from(usersTable).where(eq(usersTable.email, email)).limit(1);
  if (!user) {
    return res.json({ success: true, message: "Se o email existir, você receberá as instruções" });
  }
  const token = Math.random().toString(36).substring(2, 15);
  const expires = new Date(Date.now() + 3600000);
  await db.update(usersTable).set({
    password_reset_token: token,
    password_reset_expires: expires
  }).where(eq(usersTable.id, user.id));
  return res.json({ success: true, message: "Se o email existir, você receberá as instruções" });
});

router.post("/reset-password", async (req, res) => {
  const { token, password } = req.body;
  if (!token || !password) {
    return res.status(400).json({ error: "Token e senha obrigatórios" });
  }
  const [user] = await db.select().from(usersTable)
    .where(eq(usersTable.password_reset_token, token)).limit(1);
  if (!user || !user.password_reset_expires || user.password_reset_expires < new Date()) {
    return res.status(400).json({ error: "Token inválido ou expirado" });
  }
  const password_hash = await bcrypt.hash(password, 10);
  await db.update(usersTable).set({
    password_hash,
    password_reset_token: null,
    password_reset_expires: null
  }).where(eq(usersTable.id, user.id));
  return res.json({ success: true, message: "Senha alterada com sucesso" });
});

export default router;
