import { pgTable, serial, text, boolean, timestamp, integer } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const usersTable = pgTable("users", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull().unique(),
  password_hash: text("password_hash").notNull(),
  role: text("role").notNull().default("candidate"),
  phone: text("phone"),
  cidade: text("cidade"),
  estado: text("estado"),
  email_verified: boolean("email_verified").notNull().default(false),
  password_reset_token: text("password_reset_token"),
  password_reset_expires: timestamp("password_reset_expires"),
  is_premium: boolean("is_premium").notNull().default(false),
  premium_expires_at: timestamp("premium_expires_at"),
  stripe_customer_id: text("stripe_customer_id"),
  daily_sends_used: integer("daily_sends_used").notNull().default(0),
  last_reset_date: text("last_reset_date"),
  created_at: timestamp("created_at").notNull().defaultNow(),
});

export const insertUserSchema = createInsertSchema(usersTable).omit({ id: true, created_at: true });
export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof usersTable.$inferSelect;
