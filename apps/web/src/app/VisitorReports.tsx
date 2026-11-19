import { useEffect, useState, type FormEvent } from "react";

const path = "/api/v1/admin/visitor-reports";
type Summary = {
    session_id: string; started_at: string; ended_at: string | null; event_count: number;
};
type Report = {
    scope: "synthetic_local"; sessions: number; events: number; rows: Summary[]; next_page: number | null;
};

const day = (offset = 0) => new Date(Date.now() + offset * 86400000).toISOString().slice(0, 10);

export default function VisitorReports({ csrf }: { csrf: string }) {
    const [enabled, setEnabled] = useState(false);
    const [open, setOpen] = useState(false);
    const [start, setStart] = useState(day());
    const [until, setUntil] = useState(day(1));
    const [filter, setFilter] = useState({ start, until });
    const [page, setPage] = useState(1);
    const [data, setData] = useState<Report>();
    const [message, setMessage] = useState("");
    const [version, refresh] = useState(0);
    const params = new URLSearchParams(filter).toString();

    useEffect(() => {
        const controller = new AbortController();
        fetch("/api/v1/visitor/status", { cache: "no-store", signal: controller.signal })
            .then(response => { if (response.ok) setEnabled(true); }).catch(() => {});
        return () => controller.abort();
    }, []);

    useEffect(() => {
        if (!open) return;
        const controller = new AbortController();
        setData(undefined);
        setMessage("Đang tải báo cáo…");
        fetch(`${path}?${params}&page=${page}`, {
            cache: "no-store", credentials: "same-origin",
            signal: AbortSignal.any([controller.signal, AbortSignal.timeout(5000)]),
        }).then(async response => {
            if (!response.ok) throw new Error(String(response.status));
            const report: Report = await response.json();
            if (!controller.signal.aborted && report.scope === "synthetic_local") {
                setData(report);
                setMessage("");
            }
        }).catch(error => {
            if (!controller.signal.aborted) setMessage(`Không tải được báo cáo (${error.message}).`);
        });
        return () => controller.abort();
    }, [open, params, page, version]);

    function filterRange(event: FormEvent) {
        event.preventDefault();
        setPage(1);
        setFilter({ start, until });
        refresh(value => value + 1);
    }

    async function download(format: "csv" | "json") {
        setMessage("");
        try {
            const response = await fetch(`${path}/export?${params}&format=${format}`, {
                method: "POST", credentials: "same-origin", cache: "no-store",
                headers: { "X-Admin-CSRF": csrf }, signal: AbortSignal.timeout(8000),
            });
            if (!response.ok) throw new Error(String(response.status));
            const url = URL.createObjectURL(await response.blob());
            const link = document.createElement("a");
            link.href = url;
            link.download = `synthetic-local-sessions.${format}`;
            link.click();
            setTimeout(() => URL.revokeObjectURL(url), 1000);
        } catch (error) {
            setMessage(error instanceof Error && error.message === "413"
                ? "Báo cáo vượt giới hạn xuất. Hãy thu hẹp khoảng ngày."
                : "Không thể xuất báo cáo. Kiểm tra phiên quản trị và kết nối.");
        }
    }

    if (!enabled) return null;
    return <section aria-label="Báo cáo phiên mô phỏng">
        <button aria-expanded={open} onClick={() => setOpen(value => !value)}>
            Báo cáo phiên mô phỏng
        </button>
        {open && <>
            <h2>Báo cáo phiên mô phỏng cục bộ</h2>
            <form className="admin-form" onSubmit={filterRange}>
                <label>Từ ngày (UTC)<input type="date" required value={start} onChange={event => setStart(event.target.value)} /></label>
                <label>Đến trước ngày (UTC)<input type="date" required value={until} onChange={event => setUntil(event.target.value)} /></label>
                <button>Lọc</button>
            </form>
            {message && <p role="status">{message}</p>}
            {data && <>
                <p data-testid="visitor-totals">{data.sessions} phiên · {data.events} sự kiện</p>
                <button onClick={() => void download("csv")}>Xuất CSV</button>
                <button onClick={() => void download("json")}>Xuất JSON</button>
                <ul aria-label="Danh sách phiên">{data.rows.map(row => <li key={row.session_id}>
                    <code>{row.session_id}</code> · {row.started_at} · {row.event_count} sự kiện
                    {row.ended_at && " · Đã kết thúc"}
                </li>)}</ul>
                {page > 1 && <button onClick={() => setPage(value => value - 1)}>Trang trước</button>}
                {data.next_page !== null && <button onClick={() => setPage(data.next_page!)}>Trang sau</button>}
            </>}
        </>}
    </section>;
}
