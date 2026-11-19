import { createXRStore } from "@react-three/xr";
import type { WebGLRenderer } from "three";
import { useEffect, useRef, useState } from "react";

export const modes = ["immersive-vr", "immersive-ar"] as const;
export type Mode = typeof modes[number];
type Support = "checking" | "supported" | "unsupported" | "denied" | "unavailable" | "insecure";
type Status = "idle" | "requesting" | "active" | "ended" | "denied" | "unsupported" | "aborted" | "failed" | "context-lost";

export function sessionError(error: unknown): Status {
    const name = (error as { name?: string } | null)?.name;
    if (name === "NotAllowedError" || name === "SecurityError") return "denied";
    if (name === "NotSupportedError") return "unsupported";
    if (name === "AbortError" || name === "InvalidStateError") return "aborted";
    return "failed";
}

function createStore() {
    return createXRStore({
        offerSession: false, enterGrantedSession: false, emulate: false,
        controller: false, hand: false, gaze: false, screenInput: false, transientPointer: false,
        anchors: false, handTracking: false, layers: false, meshDetection: false,
        planeDetection: false, depthSensing: false, hitTest: true, domOverlay: false,
    });
}
export type P507XRStore = ReturnType<typeof createStore>;

export function useP507Session(clearSelection: () => void) {
    const [store, setStore] = useState<P507XRStore>();
    const [support, setSupport] = useState<Support[]>(["checking", "checking"]);
    const [requested, setRequested] = useState<Mode>();
    const [active, setActive] = useState<Mode>();
    const [status, setStatus] = useState<Status>("idle");
    const [contextLost, setContextLost] = useState(false);
    const renderer = useRef<WebGLRenderer>(undefined);
    const owner = useRef<P507XRStore>(undefined);
    const busy = useRef(false);
    const ending = useRef(false);
    const lost = useRef(false);
    const pageOpen = useRef(true);

    useEffect(() => {
        const current = createStore();
        owner.current = current;
        setStore(current);
        const unsubscribe = current.subscribe((state, previous) => {
            if (previous.session && !state.session) {
                busy.current = false;
                ending.current = false;
                setActive(undefined);
                setStatus(lost.current ? "context-lost" : "ended");
                clearSelection();
            }
        });
        const xr = navigator.xr;
        let probe = 0;
        const refresh = async () => {
            const run = ++probe;
            const results = await Promise.all(modes.map(async (mode): Promise<Support> => {
                if (!window.isSecureContext) return "insecure";
                if (!xr) return "unsupported";
                try {
                    return await xr.isSessionSupported(mode) ? "supported" : "unsupported";
                } catch (error) {
                    return sessionError(error) === "denied" ? "denied" : "unavailable";
                }
            }));
            if (run === probe) setSupport(results);
        };
        pageOpen.current = true;
        const pageHidden = () => {
            pageOpen.current = false;
            void current.getState().session?.end().catch(() => {});
        };
        const pageShown = () => { pageOpen.current = true; void refresh(); };
        void refresh();
        xr?.addEventListener("devicechange", refresh);
        window.addEventListener("focus", refresh);
        window.addEventListener("pagehide", pageHidden);
        window.addEventListener("pageshow", pageShown);
        return () => {
            ++probe;
            owner.current = undefined;
            unsubscribe();
            xr?.removeEventListener("devicechange", refresh);
            window.removeEventListener("focus", refresh);
            window.removeEventListener("pagehide", pageHidden);
            window.removeEventListener("pageshow", pageShown);
            void current.getState().session?.end().catch(() => {});
            current.destroy();
        };
    }, [clearSelection]);

    function enter(mode: Mode) {
        const current = owner.current;
        const manager = renderer.current?.xr;
        const runtime = navigator.xr;
        if (!current || !manager || !runtime || lost.current || busy.current || current.getState().session || !pageOpen.current || document.hidden ||
            !window.isSecureContext || support[modes.indexOf(mode)] !== "supported") return;
        busy.current = true;
        setRequested(mode);
        clearSelection();
        setStatus("requesting");
        // This invocation stays on the trusted click stack. Capability probing happens earlier.
        const space = mode === "immersive-ar" ? "local" : "local-floor";
        manager.setReferenceSpaceType(space);
        let opened: XRSession | undefined;
        void runtime.requestSession(mode, {
            requiredFeatures: [space],
            optionalFeatures: mode === "immersive-ar" ? ["hit-test"] : [],
        }).then(async session => {
            opened = session;
            if (owner.current !== current || lost.current || !pageOpen.current) {
                await session.end().catch(() => {});
                if (owner.current === current && !lost.current) setStatus("aborted");
                return;
            }
            await manager.setSession(session);
            if (owner.current !== current || lost.current || !pageOpen.current) {
                await session?.end().catch(() => {});
                if (owner.current === current && !lost.current) setStatus("aborted");
                return;
            }
            if (!session || current.getState().session !== session) {
                setStatus("aborted");
                return;
            }
            setActive(mode);
            setStatus("active");
        }).catch(async error => {
            await opened?.end().catch(() => {});
            if (owner.current === current && !lost.current) setStatus(sessionError(error));
        }).finally(() => {
            if (owner.current === current) busy.current = false;
        });
    }

    function exit() {
        const session = owner.current?.getState().session;
        if (!session || ending.current) return;
        ending.current = true;
        void session.end().catch(() => {
            ending.current = false;
            if (owner.current?.getState().session === session && !lost.current) setStatus("failed");
        });
    }

    function lostContext() {
        lost.current = true;
        setContextLost(true);
        setStatus("context-lost");
        clearSelection();
        exit();
    }

    function restoredContext() {
        lost.current = false;
        setContextLost(false);
        setStatus("idle");
    }

    return { store, renderer, support, requested, active, status, contextLost, enter, exit, lostContext, restoredContext };
}
