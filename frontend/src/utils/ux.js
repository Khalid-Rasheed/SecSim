/**
 * Beginner-UX helpers shared by Home / Simulator / LearnPath / Details.
 * أدوات مشتركة لتجربة المبتدئين: مستوى الصعوبة، الروابط المتقاطعة
 * (خوارزمية ← هجمتها)، وتنسيق لقطات الحالة بلغة بشرية.
 *
 * Difficulty rule (documented, deterministic):
 *   - order < 20            → beginner (classical ciphers)
 *   - brute_force           → beginner (simplest attack)
 *   - dictionary_attack     → intermediate (simple idea, richer lesson)
 *   - order < 40            → intermediate (modern ciphers, toy RSA/DH)
 *   - everything else       → advanced (hashes, KDFs, deep attacks)
 */

/** Numeric teaching order threshold below which an algorithm is "beginner". */
export const BEGINNER_MAX_ORDER = 20
/** Below this order (and not beginner) an algorithm is "intermediate". */
export const INTERMEDIATE_MAX_ORDER = 40

/**
 * Difficulty level key for an algorithm meta object.
 * @param {{id: string, order?: number}} algo registry meta (or compare entry meta)
 * @returns {'beginner'|'intermediate'|'advanced'}
 */
export function levelFor(algo) {
  if (!algo) return 'beginner'
  if (algo.id === 'brute_force') return 'beginner'
  if (algo.id === 'dictionary_attack') return 'intermediate'
  const order = algo.order ?? 100
  if (order < BEGINNER_MAX_ORDER) return 'beginner'
  if (order < INTERMEDIATE_MAX_ORDER) return 'intermediate'
  return 'advanced'
}

/**
 * Tailwind badge classes per difficulty level (color-blind safer than
 * color alone: each level also has a distinct icon in the components).
 */
export function levelBadgeClasses(level) {
  if (level === 'beginner') return 'bg-cipher/10 border-cipher/30 text-cipher'
  if (level === 'intermediate') return 'bg-keyamber/10 border-keyamber/30 text-keyamber'
  return 'bg-dangerx/10 border-dangerx/30 text-dangerx'
}

/** Font-Awesome icon per difficulty level. */
export function levelIcon(level) {
  if (level === 'beginner') return 'fa-solid fa-seedling'
  if (level === 'intermediate') return 'fa-solid fa-sprout'
  return 'fa-solid fa-mountain'
}

/**
 * Attack to try after learning an algorithm (Details page "Break it now").
 * Only broken/educational ciphers get an entry — secure ones have none.
 */
export const ATTACK_FOR = {
  caesar: 'brute_force',
  vigenere: 'vigenere_breaker',
  diffie_hellman: 'dh_mitm',
  md5: 'dictionary_attack',
  sha1: 'birthday_collision',
  sha256: 'birthday_collision',
  pbkdf2: 'dictionary_attack'
}

/**
 * Victim algorithm to read before running an attack (attack pages).
 * Inverse view of ATTACK_FOR, picked per attack id.
 */
export const VICTIM_OF = {
  brute_force: 'caesar',
  vigenere_breaker: 'vigenere',
  dh_mitm: 'diffie_hellman',
  birthday_collision: 'sha256',
  dictionary_attack: 'md5'
}

/**
 * Turn a raw snapshot key into a human label: `shared_secret` →
 * "Shared Secret". Keeps digits (`c1`) intact. No i18n lookup needed —
 * technical nouns stay Latin in both languages (consistent with the
 * rest of the bench, e.g. mono digests).
 */
export function prettyKey(key) {
  return String(key)
    .replace(/_/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

/** Max characters shown for a snapshot value before truncation. */
export const SNAP_VALUE_PREVIEW = 64

/**
 * Format one snapshot value for the readable table:
 * objects/arrays → short JSON, long strings → truncated with ellipsis,
 * booleans → ✓ / ✗. Always returns a plain display string.
 */
export function formatSnapValue(value) {
  if (typeof value === 'boolean') return value ? '✓' : '✗'
  if (value === null || value === undefined) return '—'
  if (typeof value === 'object') {
    const json = JSON.stringify(value)
    return json.length > SNAP_VALUE_PREVIEW ? json.slice(0, SNAP_VALUE_PREVIEW) + '…' : json
  }
  const text = String(value)
  return text.length > SNAP_VALUE_PREVIEW ? text.slice(0, SNAP_VALUE_PREVIEW) + '…' : text
}

/**
 * Flatten one snapshot level into [key, value] rows for the table.
 * Nested objects stay on one row (see formatSnapValue) so the table
 * never explodes on big snapshots like `attempts` lists.
 */
export function snapshotRows(snapshot) {
  if (!snapshot || typeof snapshot !== 'object') return []
  return Object.entries(snapshot).map(([key, value]) => ({
    key,
    label: prettyKey(key),
    display: formatSnapValue(value),
    full: typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)
  }))
}
