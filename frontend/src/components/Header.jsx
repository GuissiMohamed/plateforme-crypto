export default function Header({ title }) {
  return (
    <div className="border-b border-dark3 mb-6 pb-4 animate-fadeIn">
      <h1 className="text-3xl font-semibold">{title}</h1>
    </div>
  );
}
