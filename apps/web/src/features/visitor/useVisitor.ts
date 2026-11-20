import { useEffect, useState } from "react";
import {
    acknowledged, applyEvent, BATCH_SIZE, enqueue, KEY, PATH, PENDING_KEY, readLocal, readPending,
    readRemaining, readView, settled,
    type Kind, type LocalSession, type PendingStart,
} from "./session.ts";

class VisitorError extends Error {
    constructor(readonly status: number) { super(String(status)); }
}

async function request(path: string, signal: AbortSignal, method = "GET", body?: unknown) {
    const response = await fetch(PATH + path, {
        method, credentials: "same-origin", cache: "no-store",
        signal: AbortSignal.any([signal, AbortSignal.timeout(3500)]),
        headers: { "X-AIRC-Visitor": "1", ...(body === undefined ? {} : { "Content-Type": "application/json" }) },
        body: body === undefined ? undefined : JSON.stringify(body),
    });
    if (!response.ok) throw new VisitorError(response.status);
    return response.json() as Promise<unknown>;
}

const eligible = () => import.meta.env.DEV && ["127.0.0.1", "localhost", "[::1]"].includes(location.hostname);
const sessionPath = (session: LocalSession) => "/sessions/" + session.view.id;

export function useVisitor() {
    const [session, setSession] = useState<LocalSession | null>(null);
    const [pending, setPending] = useState<PendingStart | null>(null);
    const [available, setAvailable] = useState(false);
    const [suspended, setSuspended] = useState(false);
    const [message, setMessage] = useState("");
    const [actions, setActions] = useState<{
        start(previousId: string | null): void;
        record(sessionId: string, kind: Kind, object?: string): void;
        clear(sessionId: string): void;
        retry(): void;
    } | null>(null);

    useEffect(() => {
        if (!eligible()) return;
        const controller = new AbortController();
        const { signal } = controller;
        let timer: ReturnType<typeof setTimeout> | undefined;
        let pumping = false;
        let again = false;
        let attempts = 0;
        let blocked = false;

        function storageFailure() {
            if (signal.aborted) return;
            setSession(null);
            setAvailable(false);
            setMessage("Bộ nhớ trình duyệt không khả dụng. Bạn vẫn có thể dùng cảnh mẫu.");
        }

        if (!navigator.locks || !crypto.randomUUID) {
            storageFailure();
            return;
        }

        const read = () => readLocal(localStorage);
        const readStart = () => readPending(localStorage);
        function saveStart(value: PendingStart | null) {
            if (value) localStorage.setItem(PENDING_KEY, JSON.stringify(value));
            else localStorage.removeItem(PENDING_KEY);
            setPending(value);
        }
        function save(value: LocalSession | null) {
            if (value) localStorage.setItem(KEY, JSON.stringify(value));
            else localStorage.removeItem(KEY);
            setSession(value);
        }
        function locked<T>(operation: () => T | Promise<T>) {
            return navigator.locks.request(KEY, { signal }, operation);
        }

        function recover() {
            if (signal.aborted) return;
            attempts = 0;
            clearTimeout(timer);
            if (pumping) again = true;
            else void pump();
        }

        async function synchronize() {
            if (readStart()) return;
            let local = read();
            if (!local) return;
            if (local.clearing) {
                try {
                    await request(sessionPath(local), signal, "DELETE");
                } catch (error) {
                    if (!(error instanceof VisitorError && error.status === 401)) throw error;
                    setMessage("Đã xóa bộ nhớ cục bộ. Máy chủ chưa xác nhận xóa dữ liệu của phiên.");
                }
                const clearedId = local.view.id;
                await locked(() => {
                    const current = read();
                    if (current?.view.id === clearedId && current.clearing) save(null);
                });
                return;
            }
            // A bounded pass re-reads before every send so withdrawal in another tab stops the queue.
            for (let pass = 0; pass < 8; pass++) {
                local = read();
                if (!local || local.clearing || !local.queue.length) break;
                const sent = local.queue.slice(0, BATCH_SIZE);
                const sourceId = local.view.id;
                const result = await request(sessionPath(local) + "/events", signal, "POST", { events: sent });
                const ids = acknowledged(sent, result);
                const remaining = readRemaining(result as { remaining_events?: unknown });
                await locked(() => {
                    const current = read();
                    if (current?.view.id === sourceId && !current.clearing) {
                        save({
                            ...current,
                            view: { ...current.view, remaining_events: remaining },
                            queue: current.queue.filter(item => !ids.has(item.id)),
                        });
                    }
                });
            }
            local = read();
            if (!local || local.clearing) return;
            const remote = readView(await request(sessionPath(local), signal));
            await locked(() => {
                const current = read();
                if (current?.view.id === remote.id && !current.clearing) {
                    save({ ...current, proofLost: false, view: current.queue.reduce(applyEvent, remote) });
                }
            });
            setMessage("");
        }

        async function pump() {
            if (signal.aborted || !navigator.onLine || pumping) return;
            pumping = true;
            let currentId: string | undefined;
            try {
                await navigator.locks.request(KEY + ".network", { signal }, () => {
                    currentId = read()?.view.id;
                    return synchronize();
                });
                attempts = 0;
            } catch (error) {
                if (signal.aborted) return;
                if (error instanceof VisitorError && error.status === 401) {
                    await locked(() => {
                        const current = read();
                        if (!current || current.view.id !== currentId || readStart()) return;
                        save(current.queue.length ? { ...current, proofLost: true } : null);
                    }).catch(storageFailure);
                    setMessage("Mã phiên hết hiệu lực. Sự kiện chưa xác nhận vẫn được giữ. Bạn có thể dừng và xóa dữ liệu cục bộ.");
                } else if (error instanceof VisitorError && error.status < 500) {
                    if (error.status === 403 || error.status === 404) {
                        blocked = true;
                        setSuspended(true);
                        setAvailable(false);
                    }
                    setMessage(`Máy chủ từ chối đồng bộ (${error.status}). Kiểm tra hoặc xóa phiên.`);
                } else {
                    setMessage("Chưa đồng bộ được. Hàng đợi vẫn được lưu trên trình duyệt.");
                    if (attempts < 3 && navigator.onLine) {
                        timer = setTimeout(() => void pump(), 500 * 2 ** attempts++);
                    }
                }
            } finally {
                pumping = false;
                if (again && !signal.aborted) {
                    again = false;
                    recover();
                }
            }
        }

        function changed(event: StorageEvent) {
            if (event.key === KEY || event.key === PENDING_KEY || event.key === null) {
                try { setSession(read()); setPending(readStart()); } catch { storageFailure(); }
            }
        }

        try {
            const initial = read();
            setSession(initial);
            setPending(readStart());
            if (initial) recover();
        } catch {
            storageFailure();
            return;
        }

        request("/status", signal).then(() => setAvailable(true)).catch(error => {
            if (!signal.aborted && error instanceof VisitorError &&
                (error.status === 403 || error.status === 404)) {
                blocked = true;
                setSuspended(true);
            }
        });
        window.addEventListener("storage", changed);
        window.addEventListener("online", recover);
        window.addEventListener("offline", () => clearTimeout(timer), { signal });
        function start(previousId: string | null, retryOnly = false) {
            // Use the same lock order as the sync worker. No old request can race
            // rotation, and stale UI actions carry their original session ID.
            void navigator.locks.request(KEY + ".network", { signal }, () => locked(async () => {
                if (blocked) return;
                if (!navigator.onLine) {
                    setMessage("Cần kết nối để xác nhận lượt tham quan mới.");
                    return;
                }
                const existing = read();
                let attempt = readStart();
                if (!attempt) {
                    if (retryOnly || (existing?.view.id ?? null) !== previousId ||
                        (existing && !settled(existing))) return;
                    attempt = { id: crypto.randomUUID(), previousId, prepared: false };
                    saveStart(attempt); // A failed storage write must precede any network write.
                } else if (!retryOnly) return;
                if (existing?.view.id === attempt.previousId && !settled(existing)) {
                    throw new Error("The previous visit still needs confirmation");
                }

                const body = {
                    consent: "synthetic_opt_in_v1", attempt_id: attempt.id, previous_id: attempt.previousId,
                };
                if (!attempt.prepared) {
                    await request("/sessions/intent", signal, "POST", body);
                    attempt = { ...attempt, prepared: true };
                    saveStart(attempt);
                }
                const view = readView(await request("/sessions", signal, "POST", body));
                if (existing?.view.id !== view.id) {
                    const initial = { view, queue: [], clock: Date.now(), clearing: false };
                    save(enqueue(initial, "room_enter", null, Date.now(), crypto.randomUUID()));
                }
                saveStart(null);
            })).then(recover).catch(error => {
                if (!signal.aborted) setMessage(error instanceof VisitorError
                    ? `Máy chủ chưa xác nhận lượt mới (${error.status}). Yêu cầu cũ được giữ để thử lại.`
                    : "Chưa xác nhận được lượt mới. Bạn có thể thử lại hoặc tiếp tục dùng cảnh mẫu.");
            });
        }
        setActions({
            start,
            record(sessionId, kind, object) {
                void locked(() => {
                    const current = read();
                    if (blocked || readStart() || current?.view.id !== sessionId ||
                        current.clearing || current.proofLost || current.view.ended) return;
                    save(enqueue(current, kind, object ?? null, Date.now(), crypto.randomUUID()));
                }).then(recover).catch(() => {
                    if (!signal.aborted) setMessage("Không thể lưu thao tác. Kiểm tra hàng đợi trước khi tiếp tục.");
                });
            },
            clear(sessionId) {
                void locked(() => {
                    const current = read();
                    if (readStart() || current?.view.id !== sessionId) return;
                    save({
                        ...current, queue: [], clearing: true,
                        view: { ...current.view, selected_id: null, info_open: false, ended: true },
                    });
                }).then(recover).catch(storageFailure);
            },
            retry() {
                try {
                    if (readStart()) start(null, true);
                    else recover();
                } catch { storageFailure(); }
            },
        });


        return () => {
            controller.abort();
            clearTimeout(timer);
            window.removeEventListener("storage", changed);
            window.removeEventListener("online", recover);
        };
    }, []);

    return { session, pending, available, suspended, message, actions };
}
