function timestamp(value?: string | null) {
    return value && /(?:Z|[+-]\d{2}:\d{2})$/.test(value) ? Date.parse(value) : NaN;
}

export function observationAge(observed: string | null, now: number, committed?: string) {
    const observation = timestamp(observed);
    if (!Number.isFinite(observation) || !Number.isFinite(now)) return "UNKNOWN";
    const mutation = timestamp(committed);
    if (observation > now || mutation > now || observation > mutation)
        return "TIME_UNCERTAIN — hãy kiểm tra đồng hồ";
    return `${Math.floor((now - observation) / 1000)} s`;
}
