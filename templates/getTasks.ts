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

  const groups = ["Friday", "Saturday", "Sunday", "Monday", "Tuesday – Thursday"];
  const weekdayGroupIndex = [2, 3, 4, 4, 4, 0, 1];
  const currentGroup = weekdayGroupIndex[new Date().getDay()] ?? 0;
  const groupLabel = (groupIndex: number) =>
    `${((groupIndex - currentGroup + groups.length) % groups.length) + 1}. ${groups[groupIndex]}`;

  return tp.user.taskBlock(`
group by function {3: "0. This week", 0: "${groupLabel(0)}", 1: "${groupLabel(1)}", 2: "${groupLabel(2)}", 4: "${groupLabel(3)}", 5: "${groupLabel(4)}"}[task.priorityNumber]
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
