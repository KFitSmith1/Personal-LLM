'use client';

// NotebookStudio — embeds your self-hosted Open Notebook as a tab inside
// Open-Generative-AI. Copy this file into the open-generative-ai fork at:
//   components/NotebookStudio.js
//
// It renders Open Notebook (default :8502) in an iframe. Set the URL via
// NEXT_PUBLIC_NOTEBOOK_URL so it works in dev and in production.

export default function NotebookStudio() {
  const notebookUrl =
    process.env.NEXT_PUBLIC_NOTEBOOK_URL || 'http://localhost:8502';

  return (
    <div className="w-full h-[calc(100vh-72px)] bg-black">
      <iframe
        src={notebookUrl}
        className="w-full h-full border-0"
        title="Notebook Studio"
        allow="clipboard-read; clipboard-write; microphone; camera"
      />
    </div>
  );
}
