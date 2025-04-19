export default function DownloadLink({ url }) {
  return (
    <a
      href={url}
      download="flashcards.tsv"
      className="mt-4 px-4 py-2 bg-emerald-600 text-white rounded-lg"
    >
      Download TSV
    </a>
  );
}
