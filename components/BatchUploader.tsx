'use client'
import { useState } from 'react'

export default function BatchUploader({ onBatch }: { onBatch: (results:any[])=>void }) {
  const [urls, setUrls] = useState(''); const [progress, setProgress] = useState({ done:0, total:0 })
  
  async function run() {
    const list = urls.split(/\s+/).filter(Boolean)
    setProgress({ done:0, total:list.length })
    const out:any[] = []
    for (let i=0;i<list.length;i++) {
      const r = await fetch('/api/analyze', { method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({ inputType:'url', url:list[i] }) }).then(r=>r.json())
      out.push(r.data || { error:r.error, url:list[i] }); setProgress(p=>({ ...p, done: i+1 }))
    }
    onBatch(out)
  }
  
  return (
    <div className="space-y-2">
      <textarea value={urls} onChange={e=>setUrls(e.target.value)} placeholder="Un URL pe linie…" className="w-full h-32 p-2 rounded bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700"/>
      <div className="flex gap-2 items-center">
        <button onClick={run} className="px-3 py-2 rounded bg-indigo-600 text-white">Rulează batch</button>
        <span className="text-sm opacity-70">{progress.done}/{progress.total}</span>
      </div>
    </div>
  )
}