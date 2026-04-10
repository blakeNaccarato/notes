import type { App } from "./types";

/**
 * Cite selection.
 */
export default async (): Promise<string> => {
  const tp = (app as App).plugins.getPlugin("templater-obsidian").templater
    .current_functions_object;
  const text = await tp.user.getSelOrClip();
  const citation = /^\[[^]+\]\([^)]+\).*$/.test(text)
    ? text
    : `[${await tp.system.prompt("Citation name")}](${text})`;
  return `{#c: ${citation}}`;
};
