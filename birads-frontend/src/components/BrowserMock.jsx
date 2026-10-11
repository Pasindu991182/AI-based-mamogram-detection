/** Browser-chrome frame around a product screenshot, for landing-page mockups. */
export default function BrowserMock({ url = "exbi-rads.app", image, alt = "" }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl shadow-slate-900/10">
      <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50 px-4 py-2.5">
        <span className="h-2.5 w-2.5 rounded-full bg-slate-300" />
        <span className="h-2.5 w-2.5 rounded-full bg-slate-300" />
        <span className="h-2.5 w-2.5 rounded-full bg-slate-300" />
        <span className="ml-2 truncate font-mono text-[11px] text-slate-400">
          {url}
        </span>
      </div>
      <img src={image} alt={alt} className="block w-full" loading="lazy" />
    </div>
  );
}
