import type TemplaterPlugin from "templater-obsidian";
import type { Templater } from "./types";

/**
 * Get to-do list.
 */
export default async (): Promise<string[]> => {
  const tp = (
    (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
      .templater as Templater
  ).current_functions_object;
  const tags = await tp.system.prompt("Tags to include (comma-separated)");
  const excludedTags = await tp.system.prompt("Tags to exclude (comma-separated)");
  const createTagsPattern = (input: string): string =>
    String.raw`/^#(?:${input.split(/\s*(?:,|\|)\s*/).join("|")})$/`;
  const tagsPat = tags ? createTagsPattern(tags) : null;
  const excludedTagsPat = excludedTags ? createTagsPattern(excludedTags) : null;

  const common = String.raw`group by function task.tags${
    tags ? String.raw`.filter( (tag) => !${tagsPat}.test(tag) )` : ""
  }.sort().join(" ") || "#Ω-other"
( NOT done )\
AND ( ( path REGEX MATCHES /^{{ query.file.folder }}.+\.md$/ )${
    tagsPat || excludedTagsPat
      ? ` OR ( ( HAS tags )${tagsPat ? ` AND ( tag REGEX MATCHES ${tagsPat} )` : ""}${
          excludedTagsPat ? ` AND ( tag REGEX DOES NOT MATCH ${excludedTagsPat} )` : ""
        } )`
      : ""
  } )`;

  const priority = String.raw`(\
  ( status.type IS IN_PROGRESS )\
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
