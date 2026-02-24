// web/src/services/reportService.ts

// UNUSED: Only called by generateReportV1 which is also dead
export function _buildHeader(title: string): string {
  return `=== ${title.toUpperCase()} ===`;
}

// UNUSED: only called by generateReportV1 which is also dead
export function _buildFooter(title: string): string {
  return `--- ${title} ---`;
}

// UNUSED: never called from anywhere in the project
export function generateReportV1(title: string, body: string): string {
  const header = _buildHeader(title);
  const footer = _buildFooter(title);
  return `${header}\n${body}\n${footer}`;
}

// UNUSED: called inside an `if (false)` branch that never executes
export function _searchV2(query: string): string[] {
  return [`v2-result-for-${query}`];
}

export function search(query: string): string[] {
  const enableV2 = false;
  if (enableV2) {
    return _searchV2(query);
  }
  return [`basic-result-for-${query}`];
}
