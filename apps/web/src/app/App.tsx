import { lazy, Suspense } from "react";
import { ErrorBoundary } from "../components/ErrorBoundary.tsx";
const OfflineDemo = lazy(() => import("./OfflineDemo.tsx"));
const LiveApp = lazy(() => import("./LiveApp.tsx"));
export default function App() {
    const offline = new URLSearchParams(window.location.search).get("mode") === "offline";
    return <ErrorBoundary><Suspense fallback={<p role="status">Đang tải ứng dụng…</p>}>{offline ? <OfflineDemo /> : <LiveApp />}</Suspense></ErrorBoundary>;
}
