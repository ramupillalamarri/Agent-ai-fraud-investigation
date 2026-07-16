import type { Severity, CaseStatus } from "@/types";

// ─── Transactions ─────────────────────────────────────────────────────────────

export type TxStatus = "flagged" | "reviewed" | "blocked" | "cleared";
export type TxType = "card_not_present" | "card_present" | "ach_transfer" | "wire_transfer" | "crypto";

export interface Transaction {
  id: string;
  timestamp: string;
  merchant: string;
  category: string;
  amount: number;
  currency: string;
  riskScore: number;
  type: TxType;
  status: TxStatus;
  cardLast4: string;
  country: string;
}

export const MOCK_TRANSACTIONS: Transaction[] = [
  { id: "TXN-20241", timestamp: "2024-01-15 14:32:01", merchant: "Amazon.com", category: "Online Retail", amount: 1249.99, currency: "USD", riskScore: 94, type: "card_not_present", status: "flagged", cardLast4: "4821", country: "US" },
  { id: "TXN-20240", timestamp: "2024-01-15 14:18:44", merchant: "Walmart Supercenter", category: "Grocery", amount: 284.50, currency: "USD", riskScore: 23, type: "card_present", status: "cleared", cardLast4: "7392", country: "US" },
  { id: "TXN-20239", timestamp: "2024-01-15 13:55:12", merchant: "Steam Games", category: "Digital Goods", amount: 859.97, currency: "USD", riskScore: 87, type: "card_not_present", status: "flagged", cardLast4: "1104", country: "RU" },
  { id: "TXN-20238", timestamp: "2024-01-15 13:41:08", merchant: "Delta Airlines", category: "Travel", amount: 4320.00, currency: "USD", riskScore: 78, type: "card_not_present", status: "reviewed", cardLast4: "9267", country: "US" },
  { id: "TXN-20237", timestamp: "2024-01-15 13:22:33", merchant: "Coinbase Exchange", category: "Crypto", amount: 15000.00, currency: "USD", riskScore: 91, type: "crypto", status: "blocked", cardLast4: "—", country: "US" },
  { id: "TXN-20236", timestamp: "2024-01-15 12:59:17", merchant: "Target Corp", category: "Retail", amount: 112.75, currency: "USD", riskScore: 18, type: "card_present", status: "cleared", cardLast4: "6583", country: "US" },
  { id: "TXN-20235", timestamp: "2024-01-15 12:44:02", merchant: "Netflix Inc", category: "Subscription", amount: 22.99, currency: "USD", riskScore: 12, type: "card_not_present", status: "cleared", cardLast4: "2241", country: "US" },
  { id: "TXN-20234", timestamp: "2024-01-15 12:30:55", merchant: "FX Broker Ltd", category: "Finance", amount: 8750.00, currency: "USD", riskScore: 82, type: "wire_transfer", status: "flagged", cardLast4: "—", country: "CY" },
  { id: "TXN-20233", timestamp: "2024-01-15 12:15:40", merchant: "Shopify Store #4491", category: "Online Retail", amount: 399.99, currency: "USD", riskScore: 65, type: "card_not_present", status: "reviewed", cardLast4: "8830", country: "CN" },
  { id: "TXN-20232", timestamp: "2024-01-15 11:58:21", merchant: "Best Buy Co", category: "Electronics", amount: 2199.00, currency: "USD", riskScore: 72, type: "card_present", status: "reviewed", cardLast4: "5519", country: "US" },
  { id: "TXN-20231", timestamp: "2024-01-15 11:42:06", merchant: "Uber Technologies", category: "Transportation", amount: 34.80, currency: "USD", riskScore: 9, type: "card_not_present", status: "cleared", cardLast4: "3344", country: "US" },
  { id: "TXN-20230", timestamp: "2024-01-15 11:28:49", merchant: "PayPal Holdings", category: "Finance", amount: 1820.00, currency: "USD", riskScore: 55, type: "ach_transfer", status: "reviewed", cardLast4: "—", country: "US" },
  { id: "TXN-20229", timestamp: "2024-01-15 11:10:33", merchant: "Digital Ocean LLC", category: "SaaS", amount: 480.00, currency: "USD", riskScore: 31, type: "card_not_present", status: "cleared", cardLast4: "7762", country: "US" },
  { id: "TXN-20228", timestamp: "2024-01-15 10:55:17", merchant: "Binance Global", category: "Crypto", amount: 22400.00, currency: "USD", riskScore: 96, type: "crypto", status: "blocked", cardLast4: "—", country: "MT" },
  { id: "TXN-20227", timestamp: "2024-01-15 10:38:02", merchant: "Marriott Hotels", category: "Travel", amount: 1140.00, currency: "USD", riskScore: 44, type: "card_not_present", status: "cleared", cardLast4: "9908", country: "US" },
  { id: "TXN-20226", timestamp: "2024-01-15 10:22:45", merchant: "Apple Store", category: "Electronics", amount: 3299.00, currency: "USD", riskScore: 61, type: "card_present", status: "reviewed", cardLast4: "1155", country: "US" },
  { id: "TXN-20225", timestamp: "2024-01-15 10:08:29", merchant: "Anonymous Transfer", category: "Unknown", amount: 5600.00, currency: "USD", riskScore: 89, type: "wire_transfer", status: "flagged", cardLast4: "—", country: "NG" },
  { id: "TXN-20224", timestamp: "2024-01-15 09:52:14", merchant: "eBay Inc", category: "Online Retail", amount: 750.00, currency: "USD", riskScore: 58, type: "card_not_present", status: "reviewed", cardLast4: "4423", country: "US" },
  { id: "TXN-20223", timestamp: "2024-01-15 09:36:57", merchant: "CVS Health Corp", category: "Pharmacy", amount: 89.40, currency: "USD", riskScore: 14, type: "card_present", status: "cleared", cardLast4: "6617", country: "US" },
  { id: "TXN-20222", timestamp: "2024-01-15 09:21:41", merchant: "GiftCard Exchange", category: "Gift Cards", amount: 2000.00, currency: "USD", riskScore: 93, type: "card_not_present", status: "blocked", cardLast4: "8891", country: "US" },
];

// ─── Investigations ───────────────────────────────────────────────────────────

export interface Investigation {
  id: string;
  title: string;
  severity: Severity;
  status: CaseStatus;
  assignedTo: string;
  assigneeInitials: string;
  transactionCount: number;
  estimatedLoss: number;
  createdAt: string;
  updatedAt: string;
  tags: string[];
}

export const MOCK_INVESTIGATIONS: Investigation[] = [
  { id: "INV-2024-051", title: "Card Skimming Ring — Northeast Corridor", severity: "critical", status: "open", assignedTo: "Alex Morgan", assigneeInitials: "AM", transactionCount: 184, estimatedLoss: 248600, createdAt: "2024-01-14", updatedAt: "2024-01-15", tags: ["card-fraud", "organized"] },
  { id: "INV-2024-050", title: "Account Takeover — Enterprise SaaS Clients", severity: "high", status: "in_review", assignedTo: "Sarah Chen", assigneeInitials: "SC", transactionCount: 47, estimatedLoss: 92400, createdAt: "2024-01-13", updatedAt: "2024-01-15", tags: ["ato", "b2b"] },
  { id: "INV-2024-049", title: "Synthetic Identity Fraud — Auto Loans", severity: "high", status: "in_review", assignedTo: "Marcus Reid", assigneeInitials: "MR", transactionCount: 23, estimatedLoss: 187000, createdAt: "2024-01-12", updatedAt: "2024-01-14", tags: ["synthetic-id", "lending"] },
  { id: "INV-2024-048", title: "Crypto Mule Network — Exchange Laundering", severity: "critical", status: "escalated", assignedTo: "Priya Nair", assigneeInitials: "PN", transactionCount: 312, estimatedLoss: 1420000, createdAt: "2024-01-10", updatedAt: "2024-01-15", tags: ["crypto", "ml", "organized"] },
  { id: "INV-2024-047", title: "CNP Fraud Cluster — Electronics Retailers", severity: "medium", status: "open", assignedTo: "Unassigned", assigneeInitials: "—", transactionCount: 68, estimatedLoss: 34200, createdAt: "2024-01-10", updatedAt: "2024-01-11", tags: ["cnp", "retail"] },
  { id: "INV-2024-046", title: "Return Fraud Scheme — Fashion E-commerce", severity: "medium", status: "in_review", assignedTo: "James Wilson", assigneeInitials: "JW", transactionCount: 91, estimatedLoss: 28900, createdAt: "2024-01-09", updatedAt: "2024-01-13", tags: ["returns", "e-commerce"] },
  { id: "INV-2024-045", title: "BIN Attack — Regional Bank Cards", severity: "high", status: "escalated", assignedTo: "Alex Morgan", assigneeInitials: "AM", transactionCount: 1240, estimatedLoss: 560000, createdAt: "2024-01-08", updatedAt: "2024-01-15", tags: ["bin-attack", "banking"] },
  { id: "INV-2024-044", title: "Gift Card Fraud — Grocery Chain", severity: "low", status: "resolved", assignedTo: "Sarah Chen", assigneeInitials: "SC", transactionCount: 34, estimatedLoss: 8400, createdAt: "2024-01-07", updatedAt: "2024-01-12", tags: ["gift-cards", "grocery"] },
  { id: "INV-2024-043", title: "Wire Transfer Fraud — International SMBs", severity: "high", status: "open", assignedTo: "Marcus Reid", assigneeInitials: "MR", transactionCount: 12, estimatedLoss: 890000, createdAt: "2024-01-06", updatedAt: "2024-01-14", tags: ["wire", "international"] },
  { id: "INV-2024-042", title: "Social Engineering — Contact Center Exploit", severity: "medium", status: "in_review", assignedTo: "Priya Nair", assigneeInitials: "PN", transactionCount: 8, estimatedLoss: 45600, createdAt: "2024-01-05", updatedAt: "2024-01-10", tags: ["social-eng", "contact-center"] },
  { id: "INV-2024-041", title: "Loyalty Points Harvesting — Travel Rewards", severity: "low", status: "resolved", assignedTo: "James Wilson", assigneeInitials: "JW", transactionCount: 156, estimatedLoss: 12800, createdAt: "2024-01-04", updatedAt: "2024-01-09", tags: ["loyalty", "travel"] },
  { id: "INV-2024-040", title: "Phishing Campaign — Banking Credentials", severity: "high", status: "closed", assignedTo: "Alex Morgan", assigneeInitials: "AM", transactionCount: 89, estimatedLoss: 224000, createdAt: "2024-01-03", updatedAt: "2024-01-08", tags: ["phishing", "banking"] },
  { id: "INV-2024-039", title: "Triangulation Fraud — Marketplace Sellers", severity: "medium", status: "resolved", assignedTo: "Sarah Chen", assigneeInitials: "SC", transactionCount: 204, estimatedLoss: 18700, createdAt: "2024-01-02", updatedAt: "2024-01-07", tags: ["triangulation", "marketplace"] },
  { id: "INV-2024-038", title: "ACH Kiting — Fintech Startup Network", severity: "critical", status: "resolved", assignedTo: "Sarah Chen", assigneeInitials: "SC", transactionCount: 67, estimatedLoss: 84200, createdAt: "2023-12-28", updatedAt: "2024-01-05", tags: ["ach", "fintech"] },
  { id: "INV-2024-037", title: "Deepfake KYC Bypass — Digital Onboarding", severity: "critical", status: "closed", assignedTo: "Priya Nair", assigneeInitials: "PN", transactionCount: 19, estimatedLoss: 340000, createdAt: "2023-12-22", updatedAt: "2023-12-30", tags: ["deepfake", "kyc", "ai"] },
];

// ─── Analytics chart data ─────────────────────────────────────────────────────

export const FRAUD_TREND_30D = [
  { label: "Dec 17", value: 28, secondary: 8 },
  { label: "Dec 18", value: 31, secondary: 9 },
  { label: "Dec 19", value: 25, secondary: 7 },
  { label: "Dec 20", value: 29, secondary: 10 },
  { label: "Dec 21", value: 18, secondary: 5 },
  { label: "Dec 22", value: 14, secondary: 4 },
  { label: "Dec 23", value: 22, secondary: 6 },
  { label: "Dec 24", value: 34, secondary: 12 },
  { label: "Dec 25", value: 28, secondary: 9 },
  { label: "Dec 26", value: 38, secondary: 14 },
  { label: "Dec 27", value: 42, secondary: 16 },
  { label: "Dec 28", value: 45, secondary: 17 },
  { label: "Dec 29", value: 39, secondary: 13 },
  { label: "Dec 30", value: 36, secondary: 12 },
  { label: "Dec 31", value: 51, secondary: 20 },
  { label: "Jan 01", value: 44, secondary: 16 },
  { label: "Jan 02", value: 48, secondary: 18 },
  { label: "Jan 03", value: 52, secondary: 19 },
  { label: "Jan 04", value: 49, secondary: 17 },
  { label: "Jan 05", value: 55, secondary: 21 },
  { label: "Jan 06", value: 47, secondary: 18 },
  { label: "Jan 07", value: 38, secondary: 14 },
  { label: "Jan 08", value: 61, secondary: 24 },
  { label: "Jan 09", value: 58, secondary: 22 },
  { label: "Jan 10", value: 63, secondary: 25 },
  { label: "Jan 11", value: 69, secondary: 27 },
  { label: "Jan 12", value: 72, secondary: 29 },
  { label: "Jan 13", value: 65, secondary: 25 },
  { label: "Jan 14", value: 58, secondary: 23 },
  { label: "Jan 15", value: 78, secondary: 31 },
];

export const AGENT_PERFORMANCE = [
  { label: "Jan 09", value: 94 },
  { label: "Jan 10", value: 91 },
  { label: "Jan 11", value: 96 },
  { label: "Jan 12", value: 93 },
  { label: "Jan 13", value: 97 },
  { label: "Jan 14", value: 95 },
  { label: "Jan 15", value: 98 },
];

export const TX_VOLUME_WEEKLY = [
  { label: "Mon", value: 42 },
  { label: "Tue", value: 58 },
  { label: "Wed", value: 61 },
  { label: "Thu", value: 73 },
  { label: "Fri", value: 95 },
  { label: "Sat", value: 38 },
  { label: "Sun", value: 21 },
];

export const TOP_FRAUD_CATEGORIES = [
  { label: "Card Not Present", value: 38, color: "hsl(0 72% 60%)" },
  { label: "Account Takeover", value: 24, color: "hsl(25 95% 58%)" },
  { label: "Identity Theft", value: 18, color: "hsl(43 96% 56%)" },
  { label: "Return / Refund Abuse", value: 12, color: "hsl(270 67% 64%)" },
  { label: "Wire / ACH Fraud", value: 8, color: "hsl(199 89% 52%)" },
];

export const TOP_MERCHANTS_LOSS = [
  { label: "Electronics Retailers", value: 1240000, color: "hsl(0 72% 60%)" },
  { label: "Online Marketplaces", value: 890000, color: "hsl(25 95% 58%)" },
  { label: "Crypto Exchanges", value: 740000, color: "hsl(43 96% 56%)" },
  { label: "Travel Platforms", value: 480000, color: "hsl(270 67% 64%)" },
  { label: "Financial Services", value: 320000, color: "hsl(199 89% 52%)" },
];
