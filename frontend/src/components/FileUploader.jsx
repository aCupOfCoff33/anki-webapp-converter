export default function FileUploader({ onUpload }) {
    const handleChange = (e) => {
      onUpload(Array.from(e.target.files));
      e.target.value = ""; // reset
    };
    return (
      <label className="flex flex-col items-center p-6 bg-white rounded-lg shadow cursor-pointer w-72">
        <span className="text-slate-600 mb-2">Click or Drag files here</span>
        <input
          type="file"
          accept=".docx"
          multiple
          onChange={handleChange}
          className="hidden"
        />
      </label>
    );
  }