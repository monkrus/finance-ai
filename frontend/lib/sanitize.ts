import DOMPurify from 'dompurify';

/**
 * Sanitize untrusted HTML (e.g. third-party news article bodies) before it is
 * injected via `dangerouslySetInnerHTML`.
 *
 * Uses DOMPurify with the standard HTML profile: safe formatting tags
 * (paragraphs, lists, links, emphasis, headings, images, tables, code, …) are
 * preserved, while scripts, event handlers (onerror/onclick/…), `javascript:`
 * URLs, and other XSS vectors are stripped.
 */
export function sanitizeHtml(dirty: string | null | undefined): string {
  if (!dirty) return '';
  // Content is only ever rendered client-side (after the data query resolves),
  // so DOMPurify always runs with a real DOM. Fail closed on the server.
  if (typeof window === 'undefined') return '';
  return DOMPurify.sanitize(dirty, { USE_PROFILES: { html: true } });
}
