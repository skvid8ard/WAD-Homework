import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy } from 'lucide-react';
import toast from 'react-hot-toast'; // Импортируем функцию вызова уведомления

interface MarkdownMessageProps {
  content: string;
}

export const MarkdownMessage: React.FC<MarkdownMessageProps> = ({ content }) => {
  return (
    <div className="text-sm md:text-base space-y-4">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            const codeString = String(children).replace(/\n$/, '');

            // Функция копирования в буфер обмена
            const handleCopy = () => {
              navigator.clipboard.writeText(codeString);
              toast.success('Код скопирован!'); // Вызываем красивое уведомление
            };

            return !inline && match ? (
              // Обертка для блока кода с шапкой
              <div className="relative group rounded-md overflow-hidden my-4 border border-zinc-700/50">
                {/* Шапка блока кода (Язык + Кнопка) */}
                <div className="flex items-center justify-between px-4 py-1.5 bg-zinc-800/80 text-zinc-400 text-xs">
                  <span className="uppercase font-medium">{match[1]}</span>
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 hover:text-zinc-100 transition-colors py-1 px-2 rounded-md hover:bg-zinc-700"
                    title="Скопировать код"
                  >
                    <Copy size={14} />
                    <span>Copy</span>
                  </button>
                </div>
                {/* Сам код */}
                <SyntaxHighlighter
                  style={vscDarkPlus as any}
                  language={match[1]}
                  PreTag="div"
                  customStyle={{ margin: 0, borderRadius: 0 }} // Убираем скругления, так как они есть на внешней обертке
                  {...props}
                >
                  {codeString}
                </SyntaxHighlighter>
              </div>
            ) : (
              // Инлайн-код
              <code className="bg-zinc-200 dark:bg-zinc-700 px-1.5 py-0.5 rounded text-sm font-mono text-pink-600 dark:text-pink-400" {...props}>
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