import type { ParsedStatement, Statement, StatementParser } from "@/types/finance"

export class PlaceholderStatementParser implements StatementParser {
  parse(statement: Statement): ParsedStatement {
    return {
      statementId: statement.id,
      transactions: [],
      balances: [],
      confidence: 0,
      parsedAt: "Not yet parsed",
    }
  }
}
