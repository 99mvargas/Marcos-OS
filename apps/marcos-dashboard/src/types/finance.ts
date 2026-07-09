export type InstitutionType =
  | "bank"
  | "credit-union"
  | "credit-card"
  | "brokerage"
  | "robo-advisor"

export type Institution = {
  id: string
  name: string
  type: InstitutionType
  logo?: string
}

export type AccountType = "checking" | "savings" | "credit-card" | "loan" | "investment"

export type Account = {
  id: string
  institutionId: string
  name: string
  accountType: AccountType
  currentBalance: number
  availableBalance: number
  interestRate?: number
  creditLimit?: number
  lastUpdated: string
}

export type Transaction = {
  id: string
  accountId: string
  date: string
  merchant: string
  category: string
  amount: number
  pending: boolean
}

export type Investment = {
  id: string
  institutionId: string
  accountName: string
  currentValue: number
  costBasis?: number
  gainLoss?: number
}

export type RecommendationPriority = "low" | "medium" | "high"

export type Recommendation = {
  id: string
  title: string
  description: string
  priority: RecommendationPriority
  financialImpact: number
  createdAt: string
}

export type FinancialSnapshot = {
  netWorth: number
  cash: number
  investments: number
  totalDebt: number
  monthlyIncome: number
  monthlyExpenses: number
  projectedDebtFreeDate: string | null
}

export type StatementType =
  | "credit-card"
  | "checking"
  | "savings"
  | "investment"
  | "mortgage"
  | "loan"

export type StatementProcessingStatus = "not-processed" | "queued" | "processing" | "parsed" | "failed"

export type Statement = {
  id: string
  institution: string
  statementType: StatementType
  fileName: string
  uploadedAt: string
  statementDate: string
  statementPeriodStart: string
  statementPeriodEnd: string
  processingStatus: StatementProcessingStatus
}

export type ExtractedTransaction = {
  date: string
  merchant: string
  amount: number
  category?: string
}

export type ExtractedBalance = {
  label: string
  amount: number
}

export type ParsedStatement = {
  statementId: string
  transactions: ExtractedTransaction[]
  balances: ExtractedBalance[]
  confidence: number
  parsedAt: string
}

export interface StatementParser {
  parse(statement: Statement): ParsedStatement
}
