import { Router, type IRouter } from "express";
import healthRouter from "./health.js";
import authRouter from "./auth.js";
import candidatesRouter from "./candidates.js";
import jobsRouter from "./jobs.js";
import applicationsRouter from "./applications.js";
import paymentsRouter from "./payments.js";
import supportRouter from "./support.js";
import adminRouter from "./admin.js";
import recruitersRouter from "./recruiters.js";

const router: IRouter = Router();

router.use(healthRouter);
router.use("/auth", authRouter);
router.use("/candidates", candidatesRouter);
router.use("/jobs", jobsRouter);
router.use("/applications", applicationsRouter);
router.use("/payments", paymentsRouter);
router.use("/support", supportRouter);
router.use("/admin", adminRouter);
router.use("/recruiters", recruitersRouter);

export default router;
