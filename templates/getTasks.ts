import type { App } from "./types";

/**
 * Function
 *
 * @param id id
 * @param showTree showTree
 * @param showId showId
 */
export default (id: string, showTree = false, showId = false): string => {
  const tp = (app as App).plugins.getPlugin("templater-obsidian").templater
    .current_functions_object;
  const dv = (app as App).plugins.getPlugin("dataview").api;
  const { tasks } = dv.pages('"__plan/plans.md"')?.[0]?.file ?? {};
  if (!tasks) throw new Error("No tasks found");
  const identified = tasks.filter((task) => task.text.includes(`🆔 ${id}`))[0];
  if (!identified) throw new Error("No task with that ID found");
  const match = identified.text.match(/⛔\s(?<deps>[\w\d-,]+)/);
  const planned = match?.groups?.["deps"]?.split(",") ?? [];
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
