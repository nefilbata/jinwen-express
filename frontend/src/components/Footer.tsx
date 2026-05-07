export default function Footer() {
  return (
    <footer className="border-t mt-16 py-8" style={{ borderColor: 'var(--divider)' }}>
      <div className="max-w-4xl mx-auto px-6 text-center text-xs space-y-1.5" style={{ color: 'var(--fg-muted)' }}>
        <p className="m-0">金文速递 · 系统自动生成 · 仅供学术参考</p>
        <p className="m-0 opacity-60">数据来源：CNKI 期刊 RSS · Semantic Scholar · 学术机构官网</p>
      </div>
    </footer>
  );
}
