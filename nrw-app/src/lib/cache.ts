export function setCache(key: string, data: any, ttlMs: number) {
  const record = { data, expiry: Date.now() + ttlMs }
  localStorage.setItem(key, JSON.stringify(record))
}

export function getCache<T>(key: string): T | null {
  const raw = localStorage.getItem(key)
  if (!raw) return null
  const record = JSON.parse(raw)
  if (Date.now() > record.expiry) {
    localStorage.removeItem(key)
    return null
  }
  return record.data
}
