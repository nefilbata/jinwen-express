import useSWR from 'swr';
import { getDailyDigest } from '@/lib/api';
import type { DailyDigestOut } from '@/lib/types';

export function useDailyPapers(date: string) {
  const { data, error, isLoading, mutate } = useSWR<DailyDigestOut>(
    `daily-${date}`,
    () => getDailyDigest(date),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 60_000,
    }
  );

  return {
    digest: data,
    isLoading,
    isError: !!error,
    mutate,
  };
}
