import { BrowserRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Layout from "./components/layout/Layout";
import DashboardPage from "./pages/DashboardPage";
import EventsPage from "./pages/EventsPage";
import EventDetailPage from "./pages/EventDetailPage";
import NetworksPage from "./pages/NetworksPage";
import NetworkDetailPage from "./pages/NetworkDetailPage";
import ConvergencePage from "./pages/ConvergencePage";
import MapPage from "./pages/MapPage";
import ThresholdsPage from "./pages/ThresholdsPage";
import ReportsPage from "./pages/ReportsPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="events" element={<EventsPage />} />
            <Route path="events/:id" element={<EventDetailPage />} />
            <Route path="networks" element={<NetworksPage />} />
            <Route path="networks/:id" element={<NetworkDetailPage />} />
            <Route path="convergence" element={<ConvergencePage />} />
            <Route path="map" element={<MapPage />} />
            <Route path="thresholds" element={<ThresholdsPage />} />
            <Route path="reports" element={<ReportsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
