import type {
  Institution,
  Account,
  Transaction,
  Investment,
  Recommendation,
  FinancialSnapshot,
  Statement,
} from "@/types/finance"

const PLACEHOLDER_SYNCED_AT = "Not yet synced"

export const MOCK_INSTITUTIONS: Institution[] = [
  { id: "navy-federal", name: "Navy Federal", type: "credit-union" },
  { id: "penfed", name: "PenFed", type: "credit-union" },
  { id: "american-express", name: "American Express", type: "credit-card" },
  { id: "chase", name: "Chase", type: "bank" },
  { id: "capital-one", name: "Capital One", type: "bank" },
  { id: "wells-fargo", name: "Wells Fargo", type: "bank" },
  { id: "etrade", name: "E*TRADE", type: "brokerage" },
  { id: "wealthfront", name: "Wealthfront", type: "robo-advisor" },
]

export const MOCK_ACCOUNTS: Account[] = [
  {
    id: "acc-navy-federal-checking",
    institutionId: "navy-federal",
    name: "Checking",
    accountType: "checking",
    currentBalance: 0,
    availableBalance: 0,
    lastUpdated: PLACEHOLDER_SYNCED_AT,
  },
  {
    id: "acc-penfed-savings",
    institutionId: "penfed",
    name: "Savings",
    accountType: "savings",
    currentBalance: 0,
    availableBalance: 0,
    lastUpdated: PLACEHOLDER_SYNCED_AT,
  },
  {
    id: "acc-amex-card",
    institutionId: "american-express",
    name: "Platinum Card",
    accountType: "credit-card",
    currentBalance: 0,
    availableBalance: 0,
    creditLimit: 0,
    lastUpdated: PLACEHOLDER_SYNCED_AT,
  },
  {
    id: "acc-chase-checking",
    institutionId: "chase",
    name: "Total Checking",
    accountType: "checking",
    currentBalance: 0,
    availableBalance: 0,
    lastUpdated: PLACEHOLDER_SYNCED_AT,
  },
  {
    id: "acc-capital-one-card",
    institutionId: "capital-one",
    name: "Venture Card",
    accountType: "credit-card",
    currentBalance: 0,
    availableBalance: 0,
    creditLimit: 0,
    lastUpdated: PLACEHOLDER_SYNCED_AT,
  },
  {
    id: "acc-wells-fargo-savings",
    institutionId: "wells-fargo",
    name: "Savings",
    accountType: "savings",
    currentBalance: 0,
    availableBalance: 0,
    lastUpdated: PLACEHOLDER_SYNCED_AT,
  },
  {
    id: "acc-etrade-brokerage",
    institutionId: "etrade",
    name: "Brokerage",
    accountType: "investment",
    currentBalance: 0,
    availableBalance: 0,
    lastUpdated: PLACEHOLDER_SYNCED_AT,
  },
  {
    id: "acc-wealthfront-invest",
    institutionId: "wealthfront",
    name: "Automated Investing",
    accountType: "investment",
    currentBalance: 0,
    availableBalance: 0,
    lastUpdated: PLACEHOLDER_SYNCED_AT,
  },
]

export const MOCK_TRANSACTIONS: Transaction[] = [
  {
    id: "txn-placeholder-1",
    accountId: "acc-chase-checking",
    date: PLACEHOLDER_SYNCED_AT,
    merchant: "Pending sync",
    category: "Uncategorized",
    amount: 0,
    pending: true,
  },
]

export const MOCK_INVESTMENTS: Investment[] = [
  {
    id: "inv-etrade",
    institutionId: "etrade",
    accountName: "Brokerage",
    currentValue: 0,
  },
  {
    id: "inv-wealthfront",
    institutionId: "wealthfront",
    accountName: "Automated Investing",
    currentValue: 0,
  },
]

export const MOCK_RECOMMENDATIONS: Recommendation[] = [
  {
    id: "rec-placeholder-1",
    title: "Recommendations will appear once accounts are connected",
    description: "Connect an institution to receive personalized financial recommendations.",
    priority: "low",
    financialImpact: 0,
    createdAt: PLACEHOLDER_SYNCED_AT,
  },
]

export const MOCK_STATEMENTS: Statement[] = [
  {
    id: "stmt-chase-checking-1",
    institution: "Chase",
    statementType: "checking",
    fileName: "chase-checking-statement.pdf",
    uploadedAt: PLACEHOLDER_SYNCED_AT,
    statementDate: PLACEHOLDER_SYNCED_AT,
    statementPeriodStart: PLACEHOLDER_SYNCED_AT,
    statementPeriodEnd: PLACEHOLDER_SYNCED_AT,
    processingStatus: "not-processed",
  },
  {
    id: "stmt-amex-card-1",
    institution: "American Express",
    statementType: "credit-card",
    fileName: "amex-platinum-statement.pdf",
    uploadedAt: PLACEHOLDER_SYNCED_AT,
    statementDate: PLACEHOLDER_SYNCED_AT,
    statementPeriodStart: PLACEHOLDER_SYNCED_AT,
    statementPeriodEnd: PLACEHOLDER_SYNCED_AT,
    processingStatus: "not-processed",
  },
  {
    id: "stmt-penfed-savings-1",
    institution: "PenFed",
    statementType: "savings",
    fileName: "penfed-savings-statement.pdf",
    uploadedAt: PLACEHOLDER_SYNCED_AT,
    statementDate: PLACEHOLDER_SYNCED_AT,
    statementPeriodStart: PLACEHOLDER_SYNCED_AT,
    statementPeriodEnd: PLACEHOLDER_SYNCED_AT,
    processingStatus: "not-processed",
  },
  {
    id: "stmt-etrade-brokerage-1",
    institution: "E*TRADE",
    statementType: "investment",
    fileName: "etrade-brokerage-statement.pdf",
    uploadedAt: PLACEHOLDER_SYNCED_AT,
    statementDate: PLACEHOLDER_SYNCED_AT,
    statementPeriodStart: PLACEHOLDER_SYNCED_AT,
    statementPeriodEnd: PLACEHOLDER_SYNCED_AT,
    processingStatus: "not-processed",
  },
]

export const MOCK_FINANCIAL_SNAPSHOT: FinancialSnapshot = {
  netWorth: 0,
  cash: 0,
  investments: 0,
  totalDebt: 0,
  monthlyIncome: 0,
  monthlyExpenses: 0,
  projectedDebtFreeDate: null,
}
