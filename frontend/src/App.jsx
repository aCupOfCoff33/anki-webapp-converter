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
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
  
    try {
      const response = await fetch("http://localhost:8000/convert", {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) throw new Error("Conversion failed");
  
      const blob = await response.blob();
  
      // ✅ Extract filename from Content-Disposition header
      const disposition = response.headers.get("Content-Disposition");
      let fileName = "flashcards.tsv";
      if (disposition && disposition.includes("filename=")) {
        fileName = disposition
          .split("filename=")[1]
          .replace(/["']/g, "")
          .trim();
      }
  
      // ✅ Trigger download with correct filename
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Error converting file:", err);
    }
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