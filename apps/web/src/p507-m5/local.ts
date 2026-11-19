export const isLoopback = (host: string) => ["localhost", "127.0.0.1", "[::1]"].includes(host);
