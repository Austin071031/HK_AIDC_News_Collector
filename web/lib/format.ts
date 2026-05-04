export function formatClusterDate(value: string): string {
  return value ? new Date(value).toLocaleDateString("en-GB") : "Unknown date";
}
