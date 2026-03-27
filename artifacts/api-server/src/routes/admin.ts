import { Router, type IRouter } from "express";
import { db, usersTable, jobsTable, applicationsTable } from "@workspace/db";
import { eq, sql } from "drizzle-orm";
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

router.get("/stats", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const [totalUsers] = await db.select({ count: sql<number>`count(*)` }).from(usersTable);
  const [totalCandidates] = await db.select({ count: sql<number>`count(*)` }).from(usersTable).where(eq(usersTable.role, "candidate"));
  const [totalRecruiters] = await db.select({ count: sql<number>`count(*)` }).from(usersTable).where(eq(usersTable.role, "recruiter"));
  const [totalJobs] = await db.select({ count: sql<number>`count(*)` }).from(jobsTable);
  const [totalApplications] = await db.select({ count: sql<number>`count(*)` }).from(applicationsTable);
  const [premiumUsers] = await db.select({ count: sql<number>`count(*)` }).from(usersTable).where(eq(usersTable.is_premium, true));

  return res.json({
    total_users: Number(totalUsers.count),
    total_candidates: Number(totalCandidates.count),
    total_recruiters: Number(totalRecruiters.count),
    total_jobs: Number(totalJobs.count),
    total_applications: Number(totalApplications.count),
    premium_users: Number(premiumUsers.count),
  });
});

export default router;
