import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MarkdownMessageProps {
  content: string;
}

export const MarkdownMessage: React.FC<MarkdownMessageProps> = ({ content }) => {
  return (
    <div className="text-sm md:text-base space-y-4">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]} // Поддержка таблиц и зачеркиваний
        components={{
          // Перехватываем рендер тегов <code>
          // Используем any для props, так как типы react-markdown v9 могут конфликтовать с синтаксис-хайлайтером
          code({ inline, className, children, ...props }: any) {
            // Ищем язык программирования (например, language-python)
            const match = /language-(\w+)/.exec(className || '');
            
            // Если это блок кода (не инлайн) и указан язык -> красим
            return !inline && match ? (
              <SyntaxHighlighter
                style={vscDarkPlus as any}
                language={match[1]}
                PreTag="div"
                className="rounded-md my-2"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              // Иначе рендерим обычный инлайн-код (например, `переменная`)
              <code className="bg-gray-200 dark:bg-gray-700 px-1.5 py-0.5 rounded text-sm font-mono text-pink-600 dark:text-pink-400" {...props}>
                {children}
              </code>
            );
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};