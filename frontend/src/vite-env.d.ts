/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  readonly VITE_SUPABASE_URL?: string
  readonly VITE_SUPABASE_KEY?: string
  readonly VITE_GITHUB_TOKEN?: string
  readonly VITE_DEBUG?: string
  readonly VITE_ENABLE_REAL_TIME?: string
  readonly VITE_ENABLE_GITHUB_SYNC?: string
  readonly VITE_ENV?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
