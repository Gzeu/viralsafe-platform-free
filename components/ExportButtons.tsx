'use client'
import jsPDF from 'jspdf'

export function ExportButtons({ data }: { data: any[] }) {
  function toCSV(rows:any[]) {
    if (!rows || !rows.length) return
    const headers = Array.from(new Set(rows.flatMap(r=>Object.keys(r))))
    const csv = [headers.join(','), ...rows.map(r=>headers.map(h=>JSON.stringify(r[h]??'')).join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download='results.csv'; a.click()
  }
  
  function toJSON(rows:any[]) {
    const blob = new Blob([JSON.stringify(rows, null, 2)], { type: 'application/json' })
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download='results.json'; a.click()
  }
  
  function toPDF(rows:any[]) {
    const doc = new jsPDF(); let y=10
    doc.text('ViralSafe Results', 10, y); y+=10
    rows.forEach((r, i)=>{ doc.text(`${i+1}. ${r.url||r.id||'-'} - ${r.risk?.level || ''} (${r.risk?.score||''})`, 10, y); y+=8; if (y>280){ doc.addPage(); y=10 }})
    doc.save('results.pdf')
  }
  
  return (
    <div className="flex gap-2">
      <button onClick={()=>toCSV(data)} className="px-2 py-1 rounded bg-gray-200 dark:bg-gray-700">CSV</button>
      <button onClick={()=>toJSON(data)} className="px-2 py-1 rounded bg-gray-200 dark:bg-gray-700">JSON</button>
      <button onClick={()=>toPDF(data)} className="px-2 py-1 rounded bg-gray-200 dark:bg-gray-700">PDF</button>
    </div>
  )
}