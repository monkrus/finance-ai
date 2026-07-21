'use client';

import React from 'react';

/**
 * Ambient corner glow used behind the dashboard shell.
 *
 * Previously rendered an animated three.js distort-sphere. That WebGL canvas
 * lost its GPU context on some machines/headless environments and froze the
 * render thread on every authenticated page, and it fetched an external HDR
 * environment map at runtime. Replaced with a pure-CSS radial glow: same visual
 * intent (a soft blue ambient light in the top-right), but it cannot crash,
 * freeze, or make network calls. Decorative only.
 */
export function HeroBackground() {
  return (
    <div
      className="pointer-events-none absolute top-0 right-0 -z-10 h-[500px] w-[600px] overflow-hidden opacity-40 mix-blend-screen"
      aria-hidden="true"
    >
      <div
        className="absolute -top-24 -right-24 h-[500px] w-[500px] rounded-full blur-3xl"
        style={{
          background:
            'radial-gradient(circle at center, rgba(96,140,220,0.55) 0%, rgba(42,58,90,0.35) 45%, rgba(42,58,90,0) 70%)',
        }}
      />
    </div>
  );
}
