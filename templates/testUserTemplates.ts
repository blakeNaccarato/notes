import type TemplaterPlugin from "templater-obsidian";
import type { Templater } from ".";

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
  user.getEntryId();
  user.getExpenses();
  user.getFilenameDatetimeFmt();
  user.getSelOrClip();
  user.getTimeFmt();
  user.getToDo();
  user.invokedFromTemplaterCreate();
};
