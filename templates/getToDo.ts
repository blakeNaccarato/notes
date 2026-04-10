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

  const common = String.raw`group by function task.tags${
    tags ? String.raw`.filter( (tag) => !${tagsPat}.test(tag) )` : ""
  }.sort().join(" ") || "#Ω-other"
${folder ? "( NOT done ) AND " : ""}( ( path REGEX MATCHES /^{{ query.file.${folder ? "folder }}.+.md" : "path }}"}$/ )${
    tagsPat || excludedTagsPat
      ? ` OR ( ( HAS tags )${tagsPat ? ` AND ( tag REGEX MATCHES ${tagsPat} )` : ""}${
          excludedTagsPat ? ` AND ( tag REGEX DOES NOT MATCH ${excludedTagsPat} )` : ""
        } )`
      : ""
  } )`;

  const priority = String.raw`(\
  ( status.type IS IN_PROGRESS )\
  OR NOT (priority IS none)\
  OR ( ( starts BEFORE tomorrow ) AND ( ( HAS due date ) OR ( HAS scheduled date ) ) )\
)`;

  const openFence = "```tasks";
  const closeFence = "```";

  return [
    // Priority
    String.raw`${openFence}
${common}\
AND ${priority}\
${closeFence}`,
    // Other
    String.raw`${openFence}
${common}\
AND NOT ${priority}\
${closeFence}`,
  ];
};
