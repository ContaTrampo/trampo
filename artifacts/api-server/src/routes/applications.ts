import { Router, type IRouter } from "express";
import { db, applicationsTable, jobsTable, candidateProfilesTable } from "@workspace/db";
import { eq, and } from "drizzle-orm";
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

function calculateMatchScore(jobSkills: string | null, candidateSkills: string | null, jobExp: number | null, candidateExp: number | null): number {
  let score = 50;
  if (jobSkills && candidateSkills) {
    const jobSkillList = jobSkills.toLowerCase().split(",").map(s => s.trim());
    const candidateSkillList = candidateSkills.toLowerCase().split(",").map(s => s.trim());
    const matches = jobSkillList.filter(s => candidateSkillList.some(cs => cs.includes(s) || s.includes(cs)));
    if (jobSkillList.length > 0) {
      score += (matches.length / jobSkillList.length) * 40;
    }
  }
  if (jobExp !== null && candidateExp !== null) {
    if (candidateExp >= jobExp) score += 10;
    else score -= 5;
  }
  return Math.min(100, Math.max(10, Math.round(score)));
}

router.post("/", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const { job_id } = req.body;
  if (!job_id) return res.status(400).json({ error: "job_id obrigatório" });

  const [job] = await db.select().from(jobsTable).where(eq(jobsTable.id, job_id)).limit(1);
  if (!job) return res.status(404).json({ error: "Vaga não encontrada" });

  const existing = await db.select().from(applicationsTable)
    .where(and(eq(applicationsTable.user_id, userId), eq(applicationsTable.job_id, job_id))).limit(1);
  if (existing.length > 0) {
    return res.status(400).json({ error: "Você já se candidatou a esta vaga" });
  }

  const [profile] = await db.select().from(candidateProfilesTable)
    .where(eq(candidateProfilesTable.user_id, userId)).limit(1);

  const matchScore = calculateMatchScore(
    job.required_skills, profile?.skills ?? null,
    job.required_experience, profile?.years_experience ?? null
  );

  const [application] = await db.insert(applicationsTable).values({
    user_id: userId, job_id, match_score: matchScore, status: "sent"
  }).returning();

  return res.status(201).json(application);
});

router.get("/", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const { job_id } = req.query as { job_id?: string };

  let query = db.select({
    id: applicationsTable.id,
    user_id: applicationsTable.user_id,
    job_id: applicationsTable.job_id,
    match_score: applicationsTable.match_score,
    cover_letter: applicationsTable.cover_letter,
    status: applicationsTable.status,
    is_featured: applicationsTable.is_featured,
    sent_at: applicationsTable.sent_at,
    job: jobsTable,
  }).from(applicationsTable).leftJoin(jobsTable, eq(applicationsTable.job_id, jobsTable.id));

  if (job_id) {
    const apps = await query.where(eq(applicationsTable.job_id, parseInt(job_id)));
    return res.json(apps);
  }

  const apps = await query;
  return res.json(apps);
});

router.put("/:id", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const id = parseInt(req.params.id);
  const { status } = req.body;

  const [app] = await db.update(applicationsTable)
    .set({ status })
    .where(eq(applicationsTable.id, id))
    .returning();

  return res.json(app);
});

export default router;
