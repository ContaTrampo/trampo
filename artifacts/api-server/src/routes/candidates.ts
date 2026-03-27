import { Router, type IRouter } from "express";
import { db, candidateProfilesTable, applicationsTable, jobsTable } from "@workspace/db";
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

router.get("/profile", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const [profile] = await db.select().from(candidateProfilesTable)
    .where(eq(candidateProfilesTable.user_id, userId)).limit(1);

  if (!profile) {
    const [created] = await db.insert(candidateProfilesTable)
      .values({ user_id: userId }).returning();
    return res.json(created);
  }
  return res.json(profile);
});

router.put("/profile", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const {
    job_title, years_experience, seniority, salary_min, salary_max,
    availability, work_mode, bio, skills, linkedin_url, github_url,
    whatsapp, location, education
  } = req.body;

  const [existing] = await db.select().from(candidateProfilesTable)
    .where(eq(candidateProfilesTable.user_id, userId)).limit(1);

  if (!existing) {
    const [created] = await db.insert(candidateProfilesTable).values({
      user_id: userId, job_title, years_experience, seniority, salary_min, salary_max,
      availability, work_mode, bio, skills, linkedin_url, github_url, whatsapp, location, education
    }).returning();
    return res.json(created);
  }

  const [updated] = await db.update(candidateProfilesTable).set({
    job_title, years_experience, seniority, salary_min, salary_max,
    availability, work_mode, bio, skills, linkedin_url, github_url, whatsapp, location, education
  }).where(eq(candidateProfilesTable.user_id, userId)).returning();

  return res.json(updated);
});

router.get("/applications", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const apps = await db.select({
    id: applicationsTable.id,
    user_id: applicationsTable.user_id,
    job_id: applicationsTable.job_id,
    match_score: applicationsTable.match_score,
    cover_letter: applicationsTable.cover_letter,
    status: applicationsTable.status,
    is_featured: applicationsTable.is_featured,
    sent_at: applicationsTable.sent_at,
    job: {
      id: jobsTable.id,
      title: jobsTable.title,
      company: jobsTable.company,
      description: jobsTable.description,
      location: jobsTable.location,
      cidade: jobsTable.cidade,
      estado: jobsTable.estado,
      contract_type: jobsTable.contract_type,
      salary_min: jobsTable.salary_min,
      salary_max: jobsTable.salary_max,
      work_mode: jobsTable.work_mode,
      required_skills: jobsTable.required_skills,
      required_experience: jobsTable.required_experience,
      contact_email: jobsTable.contact_email,
      benefits: jobsTable.benefits,
      status: jobsTable.status,
      source: jobsTable.source,
      is_featured: jobsTable.is_featured,
      posted_at: jobsTable.posted_at,
      recruiter_id: jobsTable.recruiter_id,
    }
  })
  .from(applicationsTable)
  .leftJoin(jobsTable, eq(applicationsTable.job_id, jobsTable.id))
  .where(eq(applicationsTable.user_id, userId));

  return res.json(apps);
});

export default router;
