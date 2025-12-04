export default function Skeleton({ height = "20px", width = "100%" }) {
  return (
    <div
      className="animate-pulse bg-dark3 rounded-md"
      style={{ height, width }}
    ></div>
  );
}
