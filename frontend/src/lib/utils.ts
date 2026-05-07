import dayjs from 'dayjs';

export function formatDate(dateStr: string | null): string {
  if (!dateStr) return '';
  return dayjs(dateStr).format('YYYY年M月D日');
}

export function formatDateShort(dateStr: string): string {
  return dayjs(dateStr).format('M/D');
}

export function formatDateISO(dateStr: string): string {
  return dayjs(dateStr).format('YYYY-MM-DD');
}

export function todayISO(): string {
  return dayjs().format('YYYY-MM-DD');
}

export function yesterdayISO(): string {
  return dayjs().subtract(1, 'day').format('YYYY-MM-DD');
}

export function tomorrowISO(): string {
  return dayjs().add(1, 'day').format('YYYY-MM-DD');
}

export function isToday(dateStr: string): boolean {
  return dayjs(dateStr).isSame(dayjs(), 'day');
}

export function truncate(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen) + '...';
}

export function cn(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(' ');
}
