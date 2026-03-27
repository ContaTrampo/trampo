import { Router, type IRouter } from "express";
import { db, usersTable } from "@workspace/db";
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

router.get("/status", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const [user] = await db.select().from(usersTable).where(eq(usersTable.id, userId)).limit(1);
  if (!user) return res.status(404).json({ error: "Usuário não encontrado" });

  const isPremium = user.is_premium && (!user.premium_expires_at || user.premium_expires_at > new Date());
  const dailyLimit = isPremium ? 100 : 5;

  return res.json({
    is_premium: isPremium,
    premium_expires_at: user.premium_expires_at,
    daily_sends_used: user.daily_sends_used,
    daily_limit: dailyLimit
  });
});

router.post("/create-checkout", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });
  return res.json({
    checkout_url: "https://buy.stripe.com/trampo-premium"
  });
});

export default router;
