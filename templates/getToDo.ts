import type { App } from "./types";

/**
 * Get to-do list.
 *
 * @param folder Get unfinished tasks in folder, or all tasks in file.
 */
export default async (folder = false): Promise<string[]> => {
  const tp = (app as App).plugins.getPlugin("templater-obsidian").templater
    .current_functions_object;
  const tags = await tp.system.prompt("Tags to include (comma-separated)");
  const excludedTags = await tp.system.prompt("Tags to exclude (comma-separated)");
  const createTagsPattern = (input: string): string =>
    String.raw`/^#(?:${input.split(/\s*(?:,|\|)\s*/).join("|")})$/`;
  const tagsPat = tags ? createTagsPattern(tags) : null;
  const excludedTagsPat = excludedTags ? createTagsPattern(excludedTags) : null;

  const config = String.raw`group by function task.tags${
    tags ? String.raw`.filter( (tag) => !${tagsPat}.test(tag) )` : ""
  }.sort().join(" ") || "#Ω-other"`;

  const pathTagFilter = String.raw`( ( path REGEX MATCHES /^{{ query.file.${folder ? "folder }}.+.md" : "path }}"}$/ )${
    tagsPat || excludedTagsPat
      ? ` OR ( ( HAS tags )${tagsPat ? ` AND ( tag REGEX MATCHES ${tagsPat} )` : ""}${
          excludedTagsPat ? ` AND ( tag REGEX DOES NOT MATCH ${excludedTagsPat} )` : ""
        } )`
      : ""
  } )`;

  const priorityFilter = String.raw`(\
  ( status.type IS IN_PROGRESS )\
  OR NOT (priority IS none)\
  OR ( (starts BEFORE tomorrow) OR (scheduled BEFORE in one month) OR (due BEFORE in one month) )\
)`;

  const openFence = "```tasks";
  const closeFence = "```";

  return [
    // Priority
    String.raw`${openFence}
${config}
${pathTagFilter}\
AND ${priorityFilter}\
AND NOT ( done )\
${closeFence}`,
    // Other
    String.raw`${openFence}
${config}
${pathTagFilter}\
AND NOT ${priorityFilter}\
AND NOT ( done )\
${closeFence}`,
    // Done
    String.raw`${openFence}
${config}
${pathTagFilter}\
AND ( done )\
${closeFence}`,
  ];
};
