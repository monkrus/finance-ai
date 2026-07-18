"use client";

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { PrismLight as SyntaxHighlighter } from 'react-syntax-highlighter';
import tsx from 'react-syntax-highlighter/dist/esm/languages/prism/tsx';
import python from 'react-syntax-highlighter/dist/esm/languages/prism/python';
import vscDarkPlus from 'react-syntax-highlighter/dist/esm/styles/prism/vsc-dark-plus';

SyntaxHighlighter.registerLanguage('tsx', tsx);
SyntaxHighlighter.registerLanguage('typescript', tsx);
SyntaxHighlighter.registerLanguage('python', python);

export function MarkdownRenderer({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ node, inline, className, children, ...props }: any) {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <div className="rounded-md overflow-hidden my-4 border border-white/10">
              <div className="bg-black/80 px-4 py-1 text-xs text-muted-foreground border-b border-white/10 flex justify-between items-center">
                <span>{match[1]}</span>
              </div>
              <SyntaxHighlighter
                {...props}
                style={vscDarkPlus as any}
                language={match[1]}
                PreTag="div"
                customStyle={{ margin: 0, background: 'transparent', padding: '1rem' }}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            </div>
          ) : (
            <code {...props} className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono text-indigo-300">
              {children}
            </code>
          );
        },
        table({ children }) {
          return (
            <div className="overflow-x-auto my-4 border border-white/10 rounded-lg">
              <table className="w-full text-sm text-left">{children}</table>
            </div>
          );
        },
        th({ children }) {
          return <th className="bg-muted/50 px-4 py-2 font-semibold text-muted-foreground">{children}</th>;
        },
        td({ children }) {
          return <td className="px-4 py-2 border-t border-white/5">{children}</td>;
        }
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
