import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

// Brand teal (RGB of #0f9b8e / #115f57).
const TEAL = [15, 155, 142];
const DARK = [17, 95, 87];
const SLATE = [71, 85, 105];
const LIGHT = [148, 163, 184];

/**
 * Generate and download a professional PDF of the report.
 * @param {object} opts
 * @param {object} opts.document   structured report document from the API
 * @param {string} opts.impression the (possibly edited) impression text
 * @param {string} opts.generator  generator name (for the footer badge)
 */
function readAsDataUrl(blob) {
  if (typeof blob === "string") return Promise.resolve(blob);
  if (!blob) return Promise.resolve(null);
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("Could not read a report image."));
    reader.readAsDataURL(blob);
  });
}

async function resolveSegmentationViews(views = []) {
  return Promise.all(
    views.map(async (view) => ({
      ...view,
      original: await readAsDataUrl(view.original),
      overlay: await readAsDataUrl(view.overlay),
      mask: await readAsDataUrl(view.mask),
    }))
  );
}

export async function exportReportPdf({
  document: doc,
  impression,
  generator,
  segmentationViews = [],
}) {
  const pdf = new jsPDF({ unit: "pt", format: "a4" });
  const pageW = pdf.internal.pageSize.getWidth();
  const pageH = pdf.internal.pageSize.getHeight();
  const M = 48; // margin
  let y = M;

  const ensure = (needed) => {
    if (y + needed > pageH - 60) {
      pdf.addPage();
      y = M;
    }
  };

  // ---- Letterhead ----
  pdf.setFillColor(...TEAL);
  pdf.rect(0, 0, pageW, 6, "F");

  pdf.setFont("helvetica", "bold");
  pdf.setFontSize(17);
  pdf.setTextColor(15, 23, 42);
  pdf.text(doc?.title ?? "Mammography Radiology Report", pageW / 2, y + 6, {
    align: "center",
  });
  y += 24;
  pdf.setFont("helvetica", "normal");
  pdf.setFontSize(9.5);
  pdf.setTextColor(...LIGHT);
  pdf.text(
    doc?.subtitle ??
      "AI-Assisted Breast Cancer Decision Support System — Auto-generated report",
    pageW / 2,
    y,
    { align: "center" }
  );
  y += 14;
  pdf.setDrawColor(...TEAL);
  pdf.setLineWidth(1.2);
  pdf.line(M, y, pageW - M, y);
  y += 18;

  // ---- Metadata table ----
  if (doc?.meta?.length) {
    const rows = [];
    for (let i = 0; i < doc.meta.length; i += 2) {
      const a = doc.meta[i];
      const b = doc.meta[i + 1];
      rows.push([
        a.label,
        a.value,
        b ? b.label : "",
        b ? b.value : "",
      ]);
    }
    autoTable(pdf, {
      startY: y,
      margin: { left: M, right: M },
      body: rows,
      theme: "plain",
      styles: { fontSize: 8.5, cellPadding: 2.5, textColor: SLATE },
      columnStyles: {
        0: { fontStyle: "bold", textColor: LIGHT, cellWidth: 90 },
        1: { fontStyle: "bold", textColor: [15, 23, 42] },
        2: { fontStyle: "bold", textColor: LIGHT, cellWidth: 90 },
        3: { fontStyle: "bold", textColor: [15, 23, 42] },
      },
    });
    y = pdf.lastAutoTable.finalY + 16;
  }

  const heading = (n, text) => {
    ensure(30);
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(11);
    pdf.setTextColor(...DARK);
    pdf.text(`${n}.  ${text}`, M, y);
    y += 6;
    pdf.setDrawColor(226, 232, 240);
    pdf.setLineWidth(0.6);
    pdf.line(M, y, pageW - M, y);
    y += 12;
  };

  const paragraph = (text, opts = {}) => {
    pdf.setFont("helvetica", opts.bold ? "bold" : "normal");
    pdf.setFontSize(opts.size ?? 9.5);
    pdf.setTextColor(...(opts.color ?? SLATE));
    const lines = pdf.splitTextToSize(text, pageW - 2 * M);
    lines.forEach((ln) => {
      ensure(14);
      pdf.text(ln, M, y);
      y += 13;
    });
    y += 4;
  };

  const addSegmentationPanel = (caption, src, x, width, accent) => {
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(7);
    pdf.setTextColor(...(accent ? TEAL : LIGHT));
    pdf.text(caption.toUpperCase(), x, y);
    const top = y + 5;
    const height = 105;
    pdf.setDrawColor(...(accent ? TEAL : [226, 232, 240]));
    pdf.setLineWidth(0.8);
    pdf.setFillColor(0, 0, 0);
    pdf.rect(x, top, width, height, "FD");
    if (src) {
      const props = pdf.getImageProperties(src);
      const scale = Math.min(width / props.width, height / props.height);
      const imageW = props.width * scale;
      const imageH = props.height * scale;
      pdf.addImage(
        src,
        props.fileType || "PNG",
        x + (width - imageW) / 2,
        top + (height - imageH) / 2,
        imageW,
        imageH
      );
    } else {
      pdf.setFont("helvetica", "italic");
      pdf.setFontSize(7);
      pdf.setTextColor(...LIGHT);
      pdf.text("Result unavailable", x + width / 2, top + height / 2, {
        align: "center",
      });
    }
  };

  // ---- AI Segmentation Results ----
  if (segmentationViews.length) {
    heading(1, "AI Segmentation Results");
    const panelGap = 8;
    const panelW = (pageW - 2 * M - 2 * panelGap) / 3;
    for (const view of segmentationViews) {
      ensure(145);
      pdf.setFont("helvetica", "bold");
      pdf.setFontSize(8.5);
      pdf.setTextColor(...DARK);
      pdf.text(view.view, M, y);
      y += 12;
      addSegmentationPanel("Input · Original", view.original, M, panelW, false);
      addSegmentationPanel(
        "Attention Overlay",
        view.overlay,
        M + panelW + panelGap,
        panelW,
        true
      );
      addSegmentationPanel(
        "Output · Binary Mask",
        view.mask,
        M + 2 * (panelW + panelGap),
        panelW,
        false
      );
      y += 120;
    }
  }

  // ---- 1. Segmentation ----
  if (doc?.segmentation) {
    heading(2, "Segmentation · Tier 1 — Attention U-Net");
    paragraph(doc.segmentation);
  }

  // ---- 2. Morphological features ----
  if (doc?.features?.length) {
    heading(3, "Morphological Feature Extraction · Tier 2 (worst-case CC/MLO)");
    autoTable(pdf, {
      startY: y,
      margin: { left: M, right: M },
      head: [["Feature", "Measured value", "Interpretation"]],
      body: doc.features.map((r) => [r.feature, r.value, r.interpretation]),
      theme: "grid",
      headStyles: { fillColor: TEAL, textColor: 255, fontSize: 8.5 },
      styles: { fontSize: 8.5, cellPadding: 4, textColor: SLATE },
      alternateRowStyles: { fillColor: [244, 250, 248] },
    });
    y = pdf.lastAutoTable.finalY + 16;
  }

  // ---- 3. BI-RADS ----
  if (doc?.birads) {
    heading(4, "BI-RADS Classification · Tier 3 — Atlas-driven rule engine");
    paragraph(`Assigned category: ${doc.birads.category}`, {
      bold: true,
      color: [15, 23, 42],
    });
    paragraph(doc.birads.rationale);
    paragraph(`Recommendation: ${doc.birads.recommendation}`, {
      bold: true,
      color: DARK,
    });
  }

  // ---- 4. Case-Based Reasoning (CBR) Precedents ----
  if (doc?.cbr) {
    heading(5, "Case-Based Reasoning (CBR) · Historical Biopsy Precedents");
    paragraph(`Precedent Concordance: ${doc.cbr.concordance}`, { bold: true });
    paragraph(`ACR Recommendation: ${doc.cbr.recommendation}`);
    if (doc.cbr.matches?.length) {
      autoTable(pdf, {
        startY: y,
        margin: { left: M, right: M },
        head: [["Case ID", "Match %", "Historical BI-RADS", "Biopsy Proven Outcome"]],
        body: doc.cbr.matches.map((m) => [
          m.case_id,
          `${m.similarity_percentage}%`,
          m.ground_truth_birads,
          m.biopsy_outcome,
        ]),
        theme: "striped",
        headStyles: { fillColor: TEAL, textColor: 255, fontSize: 8.5 },
        styles: { fontSize: 8, cellPadding: 3.5, textColor: SLATE },
        columnStyles: {
          0: { fontStyle: "bold", cellWidth: 80 },
          1: { fontStyle: "bold", textColor: DARK, cellWidth: 55 },
          2: { cellWidth: 110 },
          3: { fontStyle: "bold" },
        },
      });
      y = pdf.lastAutoTable.finalY + 14;
    }
  }

  // ---- 5. ER status ----
  if (doc?.er) {
    heading(6, "ER Status Prediction · Tier 5 — ensemble model");
    autoTable(pdf, {
      startY: y,
      margin: { left: M, right: M },
      body: [
        ["Prediction", doc.er.er_result],
        ["Probability (ER+)", `${Math.round(doc.er.probability_positive * 100)}%`],
        ["Confidence level", doc.er.confidence],
        ["Inputs used", doc.er.inputs_summary],
      ],
      theme: "grid",
      styles: { fontSize: 8.5, cellPadding: 4, textColor: SLATE },
      columnStyles: {
        0: { fontStyle: "bold", fillColor: [244, 250, 248], cellWidth: 120 },
      },
    });
    y = pdf.lastAutoTable.finalY + 16;
  }

  // ---- 6. Impression ----
  heading(7, "Impression");
  paragraph(impression || doc?.impression || "—");

  // ---- Footer on every page ----
  const pages = pdf.internal.getNumberOfPages();
  const stamp = new Date().toLocaleString();
  for (let i = 1; i <= pages; i++) {
    pdf.setPage(i);
    pdf.setDrawColor(226, 232, 240);
    pdf.setLineWidth(0.6);
    pdf.line(M, pageH - 42, pageW - M, pageH - 42);
    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(7);
    pdf.setTextColor(...LIGHT);
    pdf.text(
      "Decision-support aid — radiologist sign-off required. Not for primary clinical diagnosis.",
      M,
      pageH - 30
    );
    pdf.text(
      `Generated ${stamp} · ${generator || "system"} · Page ${i}/${pages}`,
      M,
      pageH - 20
    );
  }

  // ---- Download ----
  const ref =
    doc?.meta?.find((m) => m.label === "Patient ID")?.value?.replace(/\s+/g, "_") ||
    "report";
  pdf.save(`Mammography_Report_${ref}.pdf`);
}
