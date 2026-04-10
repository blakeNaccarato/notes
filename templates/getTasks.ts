import type { Templater, TemplaterPlugin } from "./types";

/**
 * Function
 *
 * @param id id
 * @param showTree showTree
 * @param showId showId
 */
export default (id: string, showTree = false, showId = false): string => {
  const tp = (
    (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
      .templater as Templater
  ).current_functions_object;
  const dv = tp.app.plugins.getPlugin("dataview").api;
  let planned: string[] = [];
  const { tasks } = dv.page('"__plan/plans.md"')?.["file"] ?? { tasks: [] };
  const first_filtered = tasks.filter((task) => task.text.includes(`🆔 ${id}`))[0];
  if (first_filtered != undefined) {
    const match = first_filtered.text.match(/⛔\s(?<deps>[\w\d-,]+)/);
    planned = match?.groups?.["deps"]?.split(",") ?? [];
  }
  return tp.user.taskBlock(`
group by function {3: "0. This week", 0: "1. Friday", 1: "2. Saturday", 2: "3. Sunday", 4: "4. Monday", 5: "5. Tuesday – Thursday"}[task.priorityNumber]
${showTree ? "show tree" : ""}
${showId ? "full mode" : ""}
${showId ? "preset hide_date_fields" : ""}
${showId ? "show due date" : ""}
${showId ? "preset hide_non_date_fields" : ""}
${showId ? "show id" : ""}
hide task count
not done
group by function task.tags.sort().join(" ").match(/#(?:break|reward)/)
filter by function [${planned.map((id) => `'${id}'`)}].includes(task.id)`);
};
