/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_GIT_VERSION?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
