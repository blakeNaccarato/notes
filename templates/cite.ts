import type TemplaterPlugin from "templater-obsidian";
import type { Templater } from "./types";

/**
 * Cite selection.
 */
export default async (): Promise<string> => {
  const tp = (
    (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
      .templater as Templater
  ).current_functions_object;
  const text = await tp.user.getSelOrClip();
  const citation = /^\[[^]+\]\([^)]+\).*$/.test(text)
    ? text
    : `[${await tp.system.prompt("Citation name")}](${text})`;
  return `{#c: ${citation}}`;
};
