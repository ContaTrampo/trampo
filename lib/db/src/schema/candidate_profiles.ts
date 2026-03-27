import { pgTable, serial, text, integer, real, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const candidateProfilesTable = pgTable("candidate_profiles", {
  id: serial("id").primaryKey(),
  user_id: integer("user_id").notNull().unique(),
  job_title: text("job_title"),
  years_experience: integer("years_experience"),
  seniority: text("seniority"),
  salary_min: real("salary_min"),
  salary_max: real("salary_max"),
  availability: text("availability"),
  work_mode: text("work_mode"),
  bio: text("bio"),
  skills: text("skills"),
  linkedin_url: text("linkedin_url"),
  github_url: text("github_url"),
  whatsapp: text("whatsapp"),
  phone: text("phone"),
  resume_filename: text("resume_filename"),
  resume_text: text("resume_text"),
  photo_url: text("photo_url"),
  location: text("location"),
  education: text("education"),
  created_at: timestamp("created_at").notNull().defaultNow(),
});

export const insertCandidateProfileSchema = createInsertSchema(candidateProfilesTable).omit({ id: true, created_at: true });
export type InsertCandidateProfile = z.infer<typeof insertCandidateProfileSchema>;
export type CandidateProfile = typeof candidateProfilesTable.$inferSelect;
