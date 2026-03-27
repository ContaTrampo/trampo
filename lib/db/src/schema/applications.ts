import { pgTable, serial, integer, real, text, boolean, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const applicationsTable = pgTable("applications", {
  id: serial("id").primaryKey(),
  user_id: integer("user_id").notNull(),
  job_id: integer("job_id").notNull(),
  match_score: real("match_score"),
  cover_letter: text("cover_letter"),
  email_sent_to: text("email_sent_to"),
  status: text("status").notNull().default("sent"),
  is_featured: boolean("is_featured").notNull().default(false),
  sent_at: timestamp("sent_at").notNull().defaultNow(),
});

export const insertApplicationSchema = createInsertSchema(applicationsTable).omit({ id: true, sent_at: true });
export type InsertApplication = z.infer<typeof insertApplicationSchema>;
export type Application = typeof applicationsTable.$inferSelect;
