import mongoose from 'mongoose'

const MONGODB_URI = process.env.MONGODB_URI

if (!MONGODB_URI) {
  throw new Error('MONGODB_URI is missing')
}

let cached = (global as any)._mongoose

if (!cached) {
  cached = (global as any)._mongoose = { conn: null as any, promise: null as any }
}

export async function dbConnect() {
  if (cached.conn) return cached.conn
  
  if (!cached.promise) {
    cached.promise = mongoose.connect(MONGODB_URI).then(m => m)
  }
  
  cached.conn = await cached.promise
  return cached.conn
}