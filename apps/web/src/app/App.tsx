import { lazy, Suspense } from "react";
import { ErrorBoundary } from "../components/ErrorBoundary.tsx";
const OfflineDemo = lazy(() => import("./OfflineDemo.tsx"));
const LiveApp = lazy(() => import("./LiveApp.tsx"));
const P507App = import.meta.env.DEV ? lazy(() => import("./P507App.tsx")) : null;
const Visitor = import.meta.env.DEV ? lazy(() => import("../p507-m5/Visitor.tsx")) : null;
const AdminApp = import.meta.env.DEV ? lazy(() => import("./AdminApp.tsx")) : null;
import { isLoopback } from "../p507-m5/local.ts";
export default function App() {
    const visitor = import.meta.env.DEV && isLoopback(location.hostname) && new URLSearchParams(location.search).get("mode") === "p507-visit";
    const admin = import.meta.env.DEV && new URLSearchParams(window.location.search).get("mode") === "admin";
    const p507 = import.meta.env.DEV && new URLSearchParams(window.location.search).get("mode") === "p507";
    const offline = new URLSearchParams(window.location.search).get("mode") === "offline";
    return <ErrorBoundary><Suspense fallback={<p role="status">Đang tải ứng dụng…</p>}>{visitor && Visitor ? <Visitor /> : admin && AdminApp ? <AdminApp /> : p507 && P507App ? <P507App /> : offline ? <OfflineDemo /> : <LiveApp />}</Suspense></ErrorBoundary>;
}
