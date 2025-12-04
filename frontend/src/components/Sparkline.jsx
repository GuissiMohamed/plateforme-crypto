import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement);

export default function Sparkline({ data }) {
  if (!data || data.length === 0) return null;

  // Normalisation des valeurs (indépendante pour chaque crypto)
  const min = Math.min(...data);
  const max = Math.max(...data);
  const normalized = data.map((v) =>
    max - min === 0 ? 0.5 : (v - min) / (max - min)
  );

  // Couleur en fonction de la tendance
  const isUp = data[data.length - 1] >= data[0];
  const color = isUp ? "#22c55e" : "#ef4444";

  return (
    <Line
      data={{
        labels: normalized.map((_, i) => i),
        datasets: [
          {
            data: normalized,
            borderColor: color,
            backgroundColor: "transparent",
            borderWidth: 2,
            tension: 0.4,
            pointRadius: 0,
          },
        ],
      }}
      options={{
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { display: false } },
      }}
    />
  );
}
