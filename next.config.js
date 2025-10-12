/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    MONGODB_URI: process.env.MONGODB_URI,
    VIRUSTOTAL_API_KEY: process.env.VIRUSTOTAL_API_KEY,
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
    GROQ_API_KEY: process.env.GROQ_API_KEY,
    GEMINI_API_KEY: process.env.GEMINI_API_KEY,
  }
}

export default nextConfig