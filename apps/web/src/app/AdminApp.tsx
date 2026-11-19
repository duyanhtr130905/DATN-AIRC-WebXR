import { useCallback, useEffect, useState, type FormEvent } from "react";
import { P507Scene } from "./P507App.tsx";
import mapping from "./p507-mapping.json";
import { observationAge } from "../features/live/observationAge.ts";

type Login = { username: string; csrf: string };
type Provenance = {
    provenance: string; operator: string | null; source_note: string | null;
    source_observed_at: string | null; committed_at: string | null;
};
type Catalog = Provenance & {
    id: string; logical_id: string | null; version: number; name: string;
    kind: string; group_name: string; description: string; location: string;
    modeling: "MODELED" | "NOT_MODELED" | "INFO_ONLY"; archived: boolean;
};
type State = Provenance & {
    id: string; target_id: string; state_type: "room_schedule" | "equipment_status" | "exhibit_info";
    value: Record<string, string>; version: number;
};
type Snapshot = { objects: Catalog[]; states: State[] };
const base = "/api/v1/admin";
const catalogPath = base + "/p507";

class RequestError extends Error {
    constructor(readonly status: number) { super(`HTTP ${status}`); }
}

async function request<T>(path: string, method = "GET", data?: unknown, csrf?: string, signal?: AbortSignal): Promise<T> {
    const timeout = AbortSignal.timeout(8000);
    const response = await fetch(path, {
        method, credentials: "same-origin", cache: "no-store", signal: signal ? AbortSignal.any([signal, timeout]) : timeout,
        headers: data === undefined ? (csrf ? { "X-Admin-CSRF": csrf } : {})
            : { "Content-Type": "application/json", ...(csrf ? { "X-Admin-CSRF": csrf } : {}) },
        body: data === undefined ? undefined : JSON.stringify(data),
    });
    if (!response.ok) throw new RequestError(response.status);
    return response.json() as Promise<T>;
}

function message(error: unknown) {
    if (error instanceof RequestError && error.status === 409)
        return "Dữ liệu đã thay đổi hoặc thao tác xung đột. Tải lại và kiểm tra phiên bản.";
    if (error instanceof RequestError && error.status === 429)
        return "Quá nhiều lần thử. Đợi một phút rồi thử lại.";
    return error instanceof RequestError ? `Yêu cầu bị từ chối (${error.status}).` : "Máy chủ chưa khả dụng.";
}

export default function AdminApp() {
    const [account, setAccount] = useState<Login>();
    const [status, setStatus] = useState("");
    useEffect(() => {
        const controller = new AbortController();
        request<Login>(base + "/session", "GET", undefined, undefined, controller.signal)
            .then(setAccount).catch(() => {});
        return () => controller.abort();
    }, []);
    const signedOut = useCallback(() => setAccount(undefined), []);
    async function login(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const form = event.currentTarget;
        const data = new FormData(form);
        setStatus("");
        try {
            setAccount(await request<Login>(base + "/login", "POST",
                { username: data.get("username"), password: data.get("password") }));
        } catch (error) { setStatus(message(error)); }
        finally { form.reset(); }
    }
    return account ? <AdminWorkspace account={account} signedOut={signedOut} /> : <main>
        <h1>Đăng nhập quản trị P507</h1>
        <form onSubmit={login} className="admin-form">
            <label>Tên đăng nhập<input name="username" autoComplete="username" required maxLength={64} /></label>
            <label>Mật khẩu<input name="password" type="password" autoComplete="current-password" required maxLength={256} /></label>
            <button>Đăng nhập</button>
        </form>
        {status && <p role="alert">{status}</p>}
    </main>;
}

function AdminWorkspace({ account, signedOut }: { account: Login; signedOut(): void }) {
    const [snapshot, setSnapshot] = useState<Snapshot>({ objects: [], states: [] });
    const [selection, select] = useState("");
    const [search, setSearch] = useState("");
    const [group, setGroup] = useState("");
    const [kind, setKind] = useState("");
    const [statusFilter, setStatusFilter] = useState("active");
    const [sync, setSync] = useState("CONNECTING");
    const [status, setStatus] = useState("");
    const [refreshKey, refresh] = useState(0);
    useEffect(() => {
        let active = true;
        let socket: WebSocket;
        let retry: ReturnType<typeof setTimeout>;
        const controller = new AbortController();
        let latest = 0;
        function connect() {
            const url = new URL("/ws/v1/admin/p507", location.href);
            url.protocol = location.protocol === "https:" ? "wss:" : "ws:";
            socket = new WebSocket(url);
            socket.onmessage = () => {
                const attempt = ++latest;
                request<Snapshot>(catalogPath, "GET", undefined, undefined, controller.signal)
                    .then(rows => {
                        if (active && attempt === latest) { setSnapshot(rows); setSync("CONNECTED"); }
                    }).catch(error => {
                        if (!active || attempt !== latest) return;
                        if (error instanceof RequestError && error.status === 401) signedOut();
                        else { setSync("UNAVAILABLE"); socket.close(); }
                    });
            };
            socket.onclose = () => {
                if (!active) return;
                latest++;
                setSync("STALE");
                request<Login>(base + "/session", "GET", undefined, undefined, controller.signal)
                    .catch(error => { if (active && error instanceof RequestError && error.status === 401) signedOut(); });
                retry = setTimeout(connect, 1000);
            };
        }
        connect();
        return () => { active = false; controller.abort(); clearTimeout(retry); socket.close(); };
    }, [refreshKey, signedOut]);
    const selected = snapshot.objects.find(row => row.id === selection);
    useEffect(() => {
        if (selected?.archived && statusFilter !== "archived") select("");
    }, [selected, statusFilter]);
    const statusFor = (id: string) => snapshot.states.find(row => row.target_id === id && row.state_type === "equipment_status")?.value.status;
    const objects = snapshot.objects.filter(row =>
        (!group || row.group_name === group) && (!kind || row.kind === kind) &&
        (statusFilter === "archived" ? row.archived : !row.archived && (statusFilter === "active" || statusFor(row.id) === statusFilter)) &&
        [row.name, row.logical_id, row.description].some(value => value?.toLowerCase().includes(search.toLowerCase())));
    async function write(path: string, method: string, data?: unknown) {
        setStatus("");
        try {
            return await request<Catalog>(path, method, data, account.csrf);
        } catch (error) {
            if (error instanceof RequestError && error.status === 401) signedOut();
            setStatus(message(error));
        }
    }
    async function saveCatalog(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const values = new FormData(event.currentTarget);
        const source = values.get("provenance");
        const observed = values.get("observed");
        const note = values.get("source");
        if (!source && (observed || note)) {
            setStatus("Chọn nguồn dữ liệu để lưu thời điểm hoặc ghi chú mới.");
            return;
        }
        if (source === "OWNER_ENTERED" && !observed) {
            setStatus("Nhập thời điểm quan sát cho dữ liệu do Admin ghi nhận.");
            return;
        }
        const row = await write(catalogPath + "/objects" + (selected ? "/" + selected.id : ""), selected ? "PUT" : "POST", {
            name: values.get("name"), kind: values.get("kind"), group_name: values.get("group"),
            description: values.get("description"), location: values.get("location"),
            modeling: selected?.logical_id ? "MODELED" : values.get("modeling"),
            archived: values.has("archived"), expected_version: selected?.version ?? 0,
            ...(source ? { provenance: source, observed_at: observed ? new Date(String(observed)).toISOString() : null,
                source_note: note } : {}),
        });
        if (row) select(row.id);
    }
    return <main className="admin">
        <h1>Quản trị P507</h1>
        <p>{account.username} · Danh mục và quan sát riêng tư</p>
        <p role="status" data-testid="admin-sync">{sync}</p>
        <div className="admin-actions">
            <button onClick={() => refresh(value => value + 1)}>Đồng bộ lại</button>
            <button onClick={async () => { if (await write(base + "/logout", "POST")) signedOut(); }}>Đăng xuất</button>
        </div>
        {status && <p role="alert">{status}</p>}
        <div className="workspace"><P507Scene pick={id => {
            const item = snapshot.objects.find(row => row.logical_id === id && !row.archived);
            if (item) select(item.id);
        }} /><aside>
            <h2>Danh mục P507</h2>
            <label>Tìm kiếm<input value={search} onChange={event => setSearch(event.target.value)} /></label>
            <Filter label="Nhóm" choices={snapshot.objects.map(row => row.group_name)} value={group} apply={setGroup} />
            <Filter label="Loại" choices={snapshot.objects.map(row => row.kind)} value={kind} apply={setKind} />
            <label>Lọc trạng thái danh mục<select aria-label="Lọc trạng thái danh mục" value={statusFilter} onChange={event => setStatusFilter(event.target.value)}>
                <option value="active">Đang hiển thị</option><option value="archived">Đã lưu trữ</option>
                <option>available</option><option>maintenance</option><option>offline</option>
            </select></label>
            <label>Đối tượng<select aria-label="Đối tượng" value={selection} onChange={event => select(event.target.value)}>
                <option value="">Thêm đối tượng mới</option>
                {selected && (!selected.archived || statusFilter === "archived") && !objects.includes(selected) && <option value={selected.id}>{selected.name}</option>}
                {objects.map(row => <option key={row.id} value={row.id}>{row.name}</option>)}
            </select></label>
            <section className="details" data-testid="admin-panel">
                <h2>{selected?.name ?? "Thêm đối tượng mới"}</h2>
                {selected && <>
                    <p>{selected.id} · {selected.logical_id ?? selected.modeling} · v{selected.version}</p>
                    <SourceDetails row={selected} />
                    {selected.description && <p>{selected.description}</p>}
                    {selected.location && <p>{selected.location}</p>}
                </>}
                {snapshot.states.filter(row => row.target_id === selected?.id).map(row => <Observation key={row.id} row={row} />)}
            </section>
        </aside></div>
        <div className="admin-editors">
            <section>
                <h2>Thông tin danh mục</h2>
                <form key={`${selected?.id}:${selected?.version}`} className="admin-form" onSubmit={saveCatalog}>
                    <label>Tên<input name="name" defaultValue={selected?.name} maxLength={256} required /></label>
                    <label>Loại<input name="kind" defaultValue={selected?.kind} maxLength={64} required /></label>
                    <label>Nhóm<input name="group" defaultValue={selected?.group_name} maxLength={64} required /></label>
                    <label>Mô tả<textarea name="description" defaultValue={selected?.description} maxLength={512} /></label>
                    <label>Vị trí mô tả<input name="location" defaultValue={selected?.location} maxLength={256} /></label>
                    <label>Mô hình<select name="modeling" disabled={Boolean(selected?.logical_id)} defaultValue={selected?.modeling ?? "NOT_MODELED"}>
                        {selected?.logical_id && <option>MODELED</option>}<option>NOT_MODELED</option><option>INFO_ONLY</option>
                    </select></label>
                    {selected && <label><input type="checkbox" name="archived" defaultChecked={selected.archived} /> Lưu trữ đối tượng</label>}
                    <SourceSelect preserve={Boolean(selected)} />
                    <label>Thời điểm quan sát theo giờ máy<input type="datetime-local" name="observed" step="1" /></label>
                    <label>Ghi chú nguồn<input name="source" maxLength={256} /></label>
                    <button>Lưu danh mục</button>
                </form>
            </section>
            <section data-testid="admin-schedule">
                <h2>Lịch phòng</h2>
                <StateEditor type="room_schedule" target={mapping.room_id} states={snapshot.states} write={write} />
            </section>
            {selected && !selected.archived && <section key={selected.id}>
                <h2>Quan sát đối tượng</h2>
                <StateEditor type="equipment_status" target={selected.id} states={snapshot.states} write={write} />
                <StateEditor type="exhibit_info" target={selected.id} states={snapshot.states} write={write} />
            </section>}
        </div>
    </main>;
}

function Filter({ label, choices, value, apply }: { label: string; choices: string[]; value: string; apply(value: string): void }) {
    return <label>{label}<select value={value} onChange={event => apply(event.target.value)}>
        <option value="">Tất cả</option>
        {[...new Set(choices)].sort().map(choice => <option key={choice}>{choice}</option>)}
    </select></label>;
}

function SourceSelect({ preserve = false, current }: { preserve?: boolean; current?: string }) {
    const initial = current?.startsWith("SYNTHETIC_TEST") ? "SYNTHETIC_TEST"
        : current?.startsWith("OWNER_ENTERED") ? "OWNER_ENTERED" : "";
    return <label>Nguồn dữ liệu<select name="provenance" defaultValue={initial} required={!preserve}>
        <option value="">{preserve ? "Giữ nguồn hiện tại hoặc chưa rõ" : "Chọn nguồn dữ liệu"}</option>
        <option value="OWNER_ENTERED">OWNER_ENTERED / PENDING_VERIFICATION</option>
        <option value="SYNTHETIC_TEST">SYNTHETIC_TEST / NOT_AIRC</option>
    </select></label>;
}

function SourceDetails({ row }: { row: Provenance }) {
    return <>
        <p>{row.provenance} · {row.operator ?? "Chưa rõ người nhập"}</p>
        <p>Quan sát {row.source_observed_at ?? "chưa rõ"} · {observationAge(row.source_observed_at, Date.now(), row.committed_at)}</p>
        <p>Ghi nhận {row.committed_at ?? "chưa rõ"}</p>
        {row.source_note && <p>{row.source_note}</p>}
    </>;
}

function Observation({ row }: { row: State }) {
    return <div className="state-card" data-state-type={row.state_type} data-version={row.version}>
        <strong>{row.state_type} · v{row.version}</strong>
        <p>{Object.values(row.value).join(" · ")}</p>
        <SourceDetails row={row} />
    </div>;
}

function StateEditor({ type, target, states, write }: {
    type: State["state_type"]; target: string; states: State[];
    write(path: string, method: string, data?: unknown): Promise<unknown>;
}) {
    const row = states.find(row => row.target_id === target && row.state_type === type);
    const schedule = type === "room_schedule";
    const exhibit = type === "exhibit_info";
    return <>
        {schedule && row && <Observation row={row} />}
        <form aria-label={type} key={row?.version ?? 0} className="admin-form" onSubmit={event => {
            event.preventDefault();
            const data = new FormData(event.currentTarget);
            const observed = new Date(String(data.get("observed")));
            if (!Number.isFinite(observed.getTime())) return;
            void write(catalogPath + "/state", "PUT", {
                target_id: target, state_type: type, observed_at: observed.toISOString(),
                expected_version: row?.version ?? 0, source_note: data.get("source"), provenance: data.get("provenance"),
                value: exhibit ? { title: data.get("title"), text: data.get("text") }
                    : schedule ? { status: data.get("status"), activity: data.get("activity") }
                    : { status: data.get("status") },
            });
        }}>
            <h3>{exhibit ? "Thông tin trưng bày" : schedule ? "Nhập lịch phòng" : "Tình trạng thiết bị"}</h3>
            {exhibit ? <>
                <label>Tiêu đề<input name="title" maxLength={160} required defaultValue={row?.value.title} /></label>
                <label>Nội dung<textarea name="text" maxLength={800} defaultValue={row?.value.text} /></label>
            </> : <label>Trạng thái<select aria-label="Trạng thái" name="status" defaultValue={row?.value.status}>
                {(schedule ? ["free", "occupied", "closed"] : ["available", "maintenance", "offline"]).map(status => <option key={status}>{status}</option>)}
            </select></label>}
            {schedule && <label>Hoạt động<input name="activity" required maxLength={160} defaultValue={row?.value.activity} /></label>}
            <label>Thời điểm quan sát theo giờ máy<input type="datetime-local" name="observed" step="1" required /></label>
            <label>Ghi chú nguồn<input name="source" maxLength={256} defaultValue={row?.source_note ?? ""} /></label>
            <SourceSelect current={row?.provenance} />
            <button>Lưu quan sát</button>
        </form>
    </>;
}
