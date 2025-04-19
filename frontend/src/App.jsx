import { useState } from "react";
import FileUploader from "./components/FileUploader.jsx";
import FileList from "./components/FileList.jsx";
import DownloadLink from "./components/DownloadLink.jsx";

export default function App() {
  const [files, setFiles] = useState([]);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = (selected) => {
    setFiles((prev) => [...prev, ...selected]);
  };

  const handleConvert = async () => {
    if (!files.length) return;
    setLoading(true);
    const formData = new FormData();
    files.forEach((f) => formData.append("files", f));

    const res = await fetch("http://localhost:8000/convert", {
      method: "POST",
      body: formData,
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    setDownloadUrl(url);
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex flex-col items-center p-8 gap-6">
      <h1 className="text-3xl font-bold text-slate-800">Anki Flashcard Converter</h1>
      <FileUploader onUpload={handleUpload} />
      <FileList files={files} />
      <button
        onClick={handleConvert}
        disabled={loading || !files.length}
        className="px-6 py-2 rounded-lg bg-indigo-600 text-white disabled:opacity-50"
      >
        {loading ? "Converting…" : "Convert to TSV"}
      </button>
      {downloadUrl && <DownloadLink url={downloadUrl} />}
    </div>
  );
}