import * as self from "./exportService";

export function exportCsv(data: any[]): string {
  return data.map((row) => Object.values(row).join(",")).join("\n");
}

export function exportJson(data: any[]): string {
  return JSON.stringify(data);
}

export function exportXml(data: any[]): string {
  return "<data>" + data.map((r) => `<item>${r}</item>`).join("") + "</data>";
}

export function runExport(data: any[], fmt: string): string {
  const fnName = `export${fmt.charAt(0).toUpperCase()}${fmt.slice(1)}`;
  const handler = (self as any)[fnName];
  if (!handler) {
    throw new Error(`Unknown export format: ${fmt}`);
  }
  return handler(data);
}
