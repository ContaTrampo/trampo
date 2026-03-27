import { Router, type IRouter } from "express";
import { db, jobsTable } from "@workspace/db";
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

router.get("/jobs", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const jobs = await db.select().from(jobsTable)
    .where(eq(jobsTable.recruiter_id, userId))
    .orderBy(jobsTable.posted_at);

  return res.json(jobs);
});

export default router;
