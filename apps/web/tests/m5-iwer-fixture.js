import { XRDevice, metaQuest3 } from "iwer";

export function install({ noHitTest = false } = {}) {
    if (location.hostname !== "127.0.0.1") throw new Error("Loopback browser fixture only");
    const device = new XRDevice({
        ...metaQuest3,
        supportedFeatures: noHitTest ? metaQuest3.supportedFeatures.filter(feature => feature !== "hit-test")
            : metaQuest3.supportedFeatures,
    });
    device.installRuntime({ forceInstall: true });
    device.position.set(0, 1.65, 0);
    const logs = [];
    const count = new Map();
    const original = navigator.xr.requestSession.bind(navigator.xr);
    navigator.xr.requestSession = async (mode, options) => {
        logs.push({ mode, userActive: navigator.userActivation.isActive, options });
        const session = await original(mode, options);
        for (const method of ["addEventListener", "removeEventListener"]) {
            const apply = session[method].bind(session);
            session[method] = (type, ...args) => {
                if (["select", "released", "visible", "inputChanged"].includes(args[0]?.name)) {
                    const key = logs.length + ":" + type + ":" + method;
                    count.set(key, (count.get(key) ?? 0) + 1);
                }
                return apply(type, ...args);
            };
        }
        return session;
    };
    if (!noHitTest) device.installSEM(class {
        environmentCanvas = document.createElement("canvas");
        trackedPlanes = new Set();
        trackedMeshes = new Set();
        render() {}
        computeHitTestResults(ray) {
            // Deterministic synthetic horizontal tabletop. IWER owns hit-source negotiation,
            // viewer ray construction and XRHitTestResult delivery.
            const t = (0.72 - ray[13]) / -ray[9];
            if (!Number.isFinite(t) || t < 0 || t > 3) return [];
            return [new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0,
                ray[12] - ray[8] * t, 0.72, ray[14] - ray[10] * t, 1])];
        }
    });
    return { device, logs, listeners: () => Object.fromEntries(count) };
}
