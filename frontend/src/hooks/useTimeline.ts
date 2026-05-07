import useSWR from 'swr';
import { getTimeline } from '@/lib/api';
import type { TimelineDay } from '@/lib/types';

export function useTimeline(days = 30) {
  const { data, error, isLoading } = useSWR<TimelineDay[]>(
    `timeline-${days}`,
    () => getTimeline(days),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 300_000,
    }
  );

  return {
    days: data || [],
    isLoading,
    isError: !!error,
  };
}
