import type { App } from "./types";

/**
 * Test user templates.
 */
export default async (): Promise<void> => {
  const { user } = (app as App).plugins.getPlugin("templater-obsidian").templater
    .current_functions_object;
  if (!user.invokedFromTemplaterCreate()) {
    new Notice('Use "Templater: Open insert template modal"');
    return;
  }
  user.cite();
  user.getChoice("", {});
  user.getDateFmt();
  user.getDatetimeFmt();
  user.getEntry();
  user.getEntryGroups();
  user.getEntryId();
  user.getEntryMatch();
  user.getFilenameDatetimeFmt();
  user.getSelOrClip();
  user.getTasks("zzzzzz");
  user.getTimeFmt();
  user.getToDo();
  user.invokedFromTemplaterCreate();
  user.taskBlock("");
};
