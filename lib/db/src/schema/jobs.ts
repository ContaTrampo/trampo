import { pgTable, serial, text, integer, real, boolean, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const jobsTable = pgTable("jobs", {
  id: serial("id").primaryKey(),
  recruiter_id: integer("recruiter_id"),
  title: text("title").notNull(),
  company: text("company").notNull(),
  description: text("description").notNull(),
  location: text("location"),
  cidade: text("cidade"),
  estado: text("estado"),
  contract_type: text("contract_type"),
  salary_min: real("salary_min"),
  salary_max: real("salary_max"),
  work_mode: text("work_mode"),
  required_skills: text("required_skills"),
  required_experience: integer("required_experience"),
  contact_email: text("contact_email"),
  source_url: text("source_url"),
  benefits: text("benefits"),
  status: text("status").notNull().default("active"),
  source: text("source").default("manual"),
  is_featured: boolean("is_featured").notNull().default(false),
  posted_at: timestamp("posted_at").notNull().defaultNow(),
});

export const insertJobSchema = createInsertSchema(jobsTable).omit({ id: true, posted_at: true });
export type InsertJob = z.infer<typeof insertJobSchema>;
export type Job = typeof jobsTable.$inferSelect;
