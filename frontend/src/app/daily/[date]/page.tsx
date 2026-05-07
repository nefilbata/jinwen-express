import TimelineSidebar from '@/components/TimelineSidebar';
import DailyDigest from '@/components/DailyDigest';

export async function generateMetadata({ params }: { params: { date: string } }) {
  return {
    title: `金文日报 — ${params.date}`,
  };
}

export default function DailyPage({ params }: { params: { date: string } }) {
  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <div className="flex gap-8">
        <TimelineSidebar currentDate={params.date} />
        <div className="flex-1 max-w-digest mx-auto">
          <DailyDigest date={params.date} />
        </div>
      </div>
    </div>
  );
}
