import { sanitizeHtml } from '@/lib/sanitize';

describe('sanitizeHtml', () => {
  it('removes <script> tags', () => {
    const out = sanitizeHtml('<p>Hello</p><script>alert("xss")</script>');
    expect(out).toContain('Hello');
    expect(out.toLowerCase()).not.toContain('<script');
    expect(out).not.toContain('alert("xss")');
  });

  it('strips inline event handlers', () => {
    const out = sanitizeHtml('<img src="x" onerror="alert(1)">');
    expect(out.toLowerCase()).not.toContain('onerror');
    expect(out.toLowerCase()).not.toContain('alert(1)');
  });

  it('neutralizes javascript: URLs in links', () => {
    const out = sanitizeHtml('<a href="javascript:alert(1)">click</a>');
    expect(out.toLowerCase()).not.toContain('javascript:');
    expect(out).toContain('click');
  });

  it('strips onclick handlers on anchors', () => {
    const out = sanitizeHtml('<a href="#" onclick="steal()">x</a>');
    expect(out.toLowerCase()).not.toContain('onclick');
    expect(out.toLowerCase()).not.toContain('steal()');
  });

  it('removes <iframe> injections', () => {
    const out = sanitizeHtml('<iframe src="https://evil.example"></iframe><p>ok</p>');
    expect(out.toLowerCase()).not.toContain('<iframe');
    expect(out).toContain('ok');
  });

  it('preserves safe formatting markup', () => {
    const input = '<h2>Title</h2><p><strong>Bold</strong> and <em>italic</em></p><ul><li>one</li></ul>';
    const out = sanitizeHtml(input);
    expect(out).toContain('<h2>');
    expect(out).toContain('<strong>');
    expect(out).toContain('<em>');
    expect(out).toContain('<li>');
  });

  it('handles empty / nullish input safely', () => {
    expect(sanitizeHtml('')).toBe('');
    expect(sanitizeHtml(null)).toBe('');
    expect(sanitizeHtml(undefined)).toBe('');
  });

  it('removes svg-based onload vectors', () => {
    const out = sanitizeHtml('<svg><script>alert(1)</script></svg><p>safe</p>');
    expect(out.toLowerCase()).not.toContain('alert(1)');
    expect(out).toContain('safe');
  });
});
