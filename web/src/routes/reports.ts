import { Router, Request, Response } from "express";
import { formatDate } from "../utils/formatters";
import { formatMoney } from "../utils/formatters"; // UNUSED (demo): aliased unused import

export const reportsRouter = Router();

reportsRouter.get("/reports", (_req: Request, res: Response) => {
  // We use formatDate
  const date = formatDate("2024-01-01");
  // We do NOT use formatMoney
  res.json({ date });
});
