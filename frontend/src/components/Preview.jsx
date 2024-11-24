export default function Preview({ blogData }) {
  if (!blogData) return null;

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Preview</h2>
      <div className="prose" dangerouslySetInnerHTML={{ __html: blogData.content }} />
    </div>
  );
}