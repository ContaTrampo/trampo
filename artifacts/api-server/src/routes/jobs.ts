import { Router, type IRouter } from "express";
import { db, jobsTable } from "@workspace/db";
import { eq, ilike, or, and, sql } from "drizzle-orm";
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

router.get("/", async (req, res) => {
  const { search, location, work_mode, contract_type, page = "1", limit = "20" } = req.query as Record<string, string>;
  const pageNum = parseInt(page) || 1;
  const limitNum = Math.min(parseInt(limit) || 20, 100);
  const offset = (pageNum - 1) * limitNum;

  const conditions = [eq(jobsTable.status, "active")];

  if (search) {
    conditions.push(
      or(
        ilike(jobsTable.title, `%${search}%`),
        ilike(jobsTable.company, `%${search}%`),
        ilike(jobsTable.description, `%${search}%`),
        ilike(jobsTable.required_skills, `%${search}%`)
      )!
    );
  }
  if (location) {
    conditions.push(
      or(
        ilike(jobsTable.location, `%${location}%`),
        ilike(jobsTable.cidade, `%${location}%`),
        ilike(jobsTable.estado, `%${location}%`)
      )!
    );
  }
  if (work_mode) conditions.push(eq(jobsTable.work_mode, work_mode));
  if (contract_type) conditions.push(eq(jobsTable.contract_type, contract_type));

  const whereClause = and(...conditions);

  const [{ count }] = await db.select({ count: sql<number>`count(*)` })
    .from(jobsTable).where(whereClause);

  const jobs = await db.select().from(jobsTable)
    .where(whereClause)
    .orderBy(jobsTable.is_featured, jobsTable.posted_at)
    .limit(limitNum)
    .offset(offset);

  return res.json({
    jobs,
    total: Number(count),
    page: pageNum,
    total_pages: Math.ceil(Number(count) / limitNum)
  });
});

router.get("/:id", async (req, res) => {
  const id = parseInt(req.params.id);
  const [job] = await db.select().from(jobsTable).where(eq(jobsTable.id, id)).limit(1);
  if (!job) return res.status(404).json({ error: "Vaga não encontrada" });
  return res.json(job);
});

router.post("/", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const {
    title, company, description, location, cidade, estado,
    contract_type, salary_min, salary_max, work_mode,
    required_skills, required_experience, contact_email, benefits
  } = req.body;

  if (!title || !company || !description) {
    return res.status(400).json({ error: "Campos obrigatórios faltando" });
  }

  const [job] = await db.insert(jobsTable).values({
    recruiter_id: userId, title, company, description, location, cidade, estado,
    contract_type, salary_min, salary_max, work_mode, required_skills,
    required_experience, contact_email, benefits, source: "manual"
  }).returning();

  return res.status(201).json(job);
});

router.put("/:id", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const id = parseInt(req.params.id);
  const [job] = await db.select().from(jobsTable).where(eq(jobsTable.id, id)).limit(1);
  if (!job) return res.status(404).json({ error: "Vaga não encontrada" });
  if (job.recruiter_id !== userId) return res.status(403).json({ error: "Sem permissão" });

  const {
    title, company, description, location, cidade, estado,
    contract_type, salary_min, salary_max, work_mode,
    required_skills, required_experience, contact_email, benefits
  } = req.body;

  const [updated] = await db.update(jobsTable).set({
    title, company, description, location, cidade, estado,
    contract_type, salary_min, salary_max, work_mode, required_skills,
    required_experience, contact_email, benefits
  }).where(eq(jobsTable.id, id)).returning();

  return res.json(updated);
});

router.delete("/:id", async (req, res) => {
  const userId = getAuthUser(req);
  if (!userId) return res.status(401).json({ error: "Não autorizado" });

  const id = parseInt(req.params.id);
  const [job] = await db.select().from(jobsTable).where(eq(jobsTable.id, id)).limit(1);
  if (!job) return res.status(404).json({ error: "Vaga não encontrada" });
  if (job.recruiter_id !== userId) return res.status(403).json({ error: "Sem permissão" });

  await db.delete(jobsTable).where(eq(jobsTable.id, id));
  return res.json({ success: true, message: "Vaga deletada" });
});

export default router;
