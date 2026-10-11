import { FiArrowRight } from "react-icons/fi";

function ImgPanel({ caption, accent, src }) {
  return (
    <div className="flex-1">
      <div
        className={`mb-1.5 text-[11px] font-bold uppercase tracking-wide ${
          accent ? "text-brand-600" : "text-slate-400"
        }`}
      >
        {caption}
      </div>
      {/* Portrait 3:4 frame — matches mammogram orientation so the full
          image is shown large and each panel stays the same size. */}
      <div
        className={`relative aspect-[3/4] w-full overflow-hidden rounded-xl border-2 bg-black ${
          accent ? "border-brand-400" : "border-slate-200"
        }`}
      >
        {src ? (
          <img
            src={src}
            alt={caption}
            className="absolute inset-0 h-full w-full object-contain"
          />
        ) : (
          <div className="grid h-full place-items-center text-xs italic text-slate-500">
            no image
          </div>
        )}
      </div>
    </div>
  );
}

export default function SegmentStep({ result, files }) {
  return (
    <div className="space-y-10">
      {result.analyzed_views.map((v) => {
        const original = files[v.view] ? URL.createObjectURL(files[v.view]) : null;
        const overlay = v.overlay_image_base64
          ? `data:image/png;base64,${v.overlay_image_base64}`
          : null;
        const mask = v.mask_image_base64
          ? `data:image/png;base64,${v.mask_image_base64}`
          : null;
        return (
          <div key={v.view}>
            <div className="mb-3 flex items-center gap-3">
              <h3 className="text-base font-bold text-slate-800">{v.view}</h3>
              <span
                className={`rounded-full px-2.5 py-0.5 text-xs font-bold uppercase ${
                  v.predicted_class === "Mass Detected"
                    ? "bg-red-100 text-red-600"
                    : "bg-emerald-100 text-emerald-600"
                }`}
              >
                {v.predicted_class}
              </span>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-[1fr_auto_1fr_auto_1fr] sm:items-center">
              <ImgPanel caption="Input · original" src={original} />
              <div className="hidden place-self-center pt-6 text-brand-500 sm:block">
                <FiArrowRight size={22} />
              </div>
              <ImgPanel caption="Attention overlay" src={overlay} accent />
              <div className="hidden place-self-center pt-6 text-brand-500 sm:block">
                <FiArrowRight size={22} />
              </div>
              <ImgPanel caption="Output · binary mask" src={mask} />
            </div>
          </div>
        );
      })}
      <p className="rounded-lg bg-brand-50 px-3 py-2 text-xs text-brand-700">
        The attention map lights up only the lesion — not the whole breast. The
        worst of CC/MLO is carried forward to feature extraction.
      </p>
    </div>
  );
}
