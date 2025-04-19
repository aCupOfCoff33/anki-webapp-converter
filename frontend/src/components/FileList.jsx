export default function FileList({ files }) {
  if (!files.length) return null;
  return (
    <ul className="w-72 bg-white rounded-lg shadow divide-y">
      {files.map((f, idx) => (
        <li key={idx} className="px-4 py-2 text-sm text-slate-700 truncate">
          {f.name}
        </li>
      ))}
    </ul>
  );
}
