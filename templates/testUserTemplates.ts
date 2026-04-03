import type { Templater, TemplaterPlugin } from "./types";

/**
 * Test user templates.
 */
export default async (): Promise<void> => {
  const { user } = (
    (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
      .templater as Templater
  ).current_functions_object;
  if (!user.invokedFromTemplaterCreate()) {
    new Notice('Use "Templater: Open insert template modal"');
    return;
  }
  user.cite();
  user.getChoice("", {});
  user.getExpenses();
  user.getDateFmt();
  user.getDatetimeFmt();
  user.getEntry();
  user.getEntryGroups();
  user.getEntryId();
  user.getEntryMatch();
  user.getExpenses();
  user.getFilenameDatetimeFmt();
  user.getSelOrClip();
  user.getTasks("zzzzzz");
  user.getTimeFmt();
  user.getToDo();
  user.invokedFromTemplaterCreate();
  user.taskBlock("");
};
