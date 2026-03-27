import { Router, type IRouter } from "express";
import { db, supportTicketsTable } from "@workspace/db";
import { eq } from "drizzle-orm";
import { verifyToken } from "./auth.js";

const router: IRouter = Router();

function getAuthUser(req: any): number | null {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith("Bearer ")) return null;
  try {
    const { userId } = verifyToken(authHeader.slice(7));
    return userId;
  } catch {
    return null;
  }
}

router.get("/tickets", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const tickets = await db.select().from(supportTicketsTable)
    .where(eq(supportTicketsTable.user_id, userId))
    .orderBy(supportTicketsTable.created_at);

  return res.json(tickets);
});

router.post("/tickets", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const { subject, message } = req.body;
  if (!subject || !message) {
    return res.status(400).json({ error: "Assunto e mensagem obrigatórios" });
  }

  const [ticket] = await db.insert(supportTicketsTable).values({
    user_id: userId, subject, message, status: "open", priority: "normal"
  }).returning();

  return res.status(201).json(ticket);
});

export default router;
