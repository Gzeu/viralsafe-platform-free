'use client'
import { useState } from 'react'

export default function AnalyzeForm({ onResult }: { onResult: (r:any)=>void }) {
  const [inputType, setInputType] = useState<'text'|'url'>('text')
  const [content, setContent] = useState(''), [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false), [error, setError] = useState<string| null>(null)
  
  async function submit() {
    setLoading(true); setError(null)
    try {
      const res = await fetch('/api/analyze', { method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({ inputType, content, url }) })
      const json = await res.json(); if (!json.ok) throw new Error(json.error)
      onResult(json.data)
    } catch (e:any) { setError(e.message) } finally { setLoading(false) }
  }
  
  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <button onClick={()=>setInputType('text')} className={`px-3 py-1 rounded ${inputType==='text'?'bg-blue-600 text-white':'bg-gray-200 dark:bg-gray-700'}`}>Text</button>
        <button onClick={()=>setInputType('url')} className={`px-3 py-1 rounded ${inputType==='url'?'bg-blue-600 text-white':'bg-gray-200 dark:bg-gray-700'}`}>URL</button>
      </div>
      {inputType==='text'
        ? <textarea value={content} onChange={e=>setContent(e.target.value)} maxLength={5000} className="w-full h-36 p-3 rounded bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700" placeholder="Lipește textul…" />
        : <input value={url} onChange={e=>setUrl(e.target.value)} className="w-full p-3 rounded bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700" placeholder="https://…" />
      }
      <div className="flex items-center gap-2">
        <button disabled={loading} onClick={submit} className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-50">{loading?'Analizez…':'Analizează'}</button>
        {error && <span className="text-red-500">{error}</span>}
      </div>
    </div>
  )
}