import { useEffect, useState } from "react";
import {
    acknowledged, applyEvent, BATCH_SIZE, enqueue, KEY, PATH, readLocal, readView,
    type Kind, type LocalSession,
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
    const [available, setAvailable] = useState(false);
    const [suspended, setSuspended] = useState(false);
    const [message, setMessage] = useState("");
    const [actions, setActions] = useState<{
        start(): void; record(kind: Kind, object?: string): void; clear(): void; retry(): void;
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
            let local = read();
            if (!local) return;
            if (local.clearing) {
                try {
                    await request(sessionPath(local), signal, "DELETE");
                } catch (error) {
                    if (!(error instanceof VisitorError && error.status === 401)) throw error;
                    setMessage("Đã xóa bộ nhớ cục bộ. Máy chủ không còn chấp nhận mã khôi phục.");
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
                await locked(() => {
                    const current = read();
                    if (current?.view.id === sourceId && !current.clearing) {
                        save({ ...current, queue: current.queue.filter(item => !ids.has(item.id)) });
                    }
                });
            }
            local = read();
            if (!local || local.clearing) return;
            const remote = readView(await request(sessionPath(local), signal));
            await locked(() => {
                const current = read();
                if (current?.view.id === remote.id && !current.clearing) {
                    save({ ...current, view: current.queue.reduce(applyEvent, remote) });
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
                        if (read()?.view.id === currentId) save(null);
                    }).catch(storageFailure);
                    setMessage("Phiên đã hết hiệu lực. Hàng đợi cũ đã được xóa.");
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
            if (event.key === KEY || event.key === null) {
                try { setSession(read()); } catch { storageFailure(); }
            }
        }

        try {
            const initial = read();
            setSession(initial);
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
        setActions({
            start() {
                void locked(async () => {
                    const existing = read();
                    if (existing) {
                        setSession(existing);
                        return;
                    }
                    // Check both read and write capability before asking the server to persist.
                    localStorage.setItem(KEY + ".probe", "1");
                    localStorage.removeItem(KEY + ".probe");
                    const view = readView(await request("/sessions", signal, "POST", {
                        consent: "synthetic_opt_in_v1",
                    }));
                    const initial = { view, queue: [], clock: Date.now(), clearing: false };
                    save(enqueue(initial, "room_enter", null, Date.now(), crypto.randomUUID()));
                }).then(recover).catch(error => {
                    if (!signal.aborted) setMessage(error instanceof VisitorError
                        ? `Không thể bắt đầu phiên (${error.status}).`
                        : "Không thể bắt đầu hoặc lưu phiên. Bạn vẫn có thể dùng cảnh mẫu.");
                });
            },
            record(kind, object) {
                void locked(() => {
                    const current = read();
                    if (blocked || !current || current.clearing || current.view.ended) return;
                    save(enqueue(current, kind, object ?? null, Date.now(), crypto.randomUUID()));
                }).then(recover).catch(() => {
                    if (!signal.aborted) setMessage("Không thể lưu thao tác. Kiểm tra hàng đợi trước khi tiếp tục.");
                });
            },
            clear() {
                void locked(() => {
                    const current = read();
                    if (!current) return;
                    save({
                        ...current, queue: [], clearing: true,
                        view: { ...current.view, selected_id: null, info_open: false, ended: true },
                    });
                }).then(recover).catch(storageFailure);
            },
            retry: recover,
        });

        return () => {
            controller.abort();
            clearTimeout(timer);
            window.removeEventListener("storage", changed);
            window.removeEventListener("online", recover);
        };
    }, []);

    return { session, available, suspended, message, actions };
}
