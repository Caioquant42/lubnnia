/// <reference no-default-lib="true" />
/// <reference lib="deno.ns" />

export type DenoGlobal = typeof globalThis & {
  Deno: {
    serve: (handler: (req: Request) => Response | Promise<Response>) => void;
    env: {
      get(key: string): string | undefined;
      set(key: string, value: string): void;
      toObject(): { [key: string]: string };
    };
  };
};

declare global {
  interface Window extends DenoGlobal {}
}
