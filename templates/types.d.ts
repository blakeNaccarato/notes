export type { default as TemplaterPlugin } from "templater-obsidian";

import type { Moment } from "moment";
import type { InternalModuleFile } from "templater-obsidian/dist/core/functions/internal_functions/file/InternalModuleFile";
import type { InternalModuleSystem } from "templater-obsidian/dist/core/functions/internal_functions/system/InternalModuleSystem";

/**
 * Templater interface.
 */
export interface Templater {
  current_functions_object: {
    obsidian: {
      moment: () => Moment;
    };
    user: {
      cite: (typeof import("./cite"))["default"];
      getDateFmt: (typeof import("./getDateFmt"))["default"];
      getChoice: (typeof import("./getChoice"))["default"];
      getDatetimeFmt: (typeof import("./getDatetimeFmt"))["default"];
      getEntry: (typeof import("./getEntry"))["default"];
      getEntryGroups: (typeof import("./getEntryGroups"))["default"];
      getEntryMatch: (typeof import("./getEntryMatch"))["default"];
      getEntryId: (typeof import("./getEntryId"))["default"];
      getExpenses: (typeof import("./getExpenses"))["default"];
      getFilenameDatetimeFmt: (typeof import("./getFilenameDatetimeFmt"))["default"];
      getSelOrClip: (typeof import("./getSelOrClip"))["default"];
      getTasks: (typeof import("./getTasks"))["default"];
      getTimeFmt: (typeof import("./getTimeFmt"))["default"];
      getToDo: (typeof import("./getToDo"))["default"];
      invokedFromTemplaterCreate: (typeof import("./invokedFromTemplaterCreate"))["default"];
      taskBlock: (typeof import("./taskBlock"))["default"];
      testUserTemplates: (typeof import("./testUserTemplates"))["default"];
    };
    file: {
      content: Content;
      path: Path;
      selection: Selection;
    };
    system: {
      clipboard: Clipboard;
      prompt: Prompt;
      suggester: Suggester;
    };
  };
}

type ContentGenerator = ReturnType<
  InstanceType<typeof InternalModuleFile>["generate_selection"]
>;
type Content = Awaited<
  (...args: Partial<Parameters<ContentGenerator>>) => ReturnType<ContentGenerator>
>;

type PathGenerator = ReturnType<
  InstanceType<typeof InternalModuleFile>["generate_path"]
>;
type Path = (...args: Partial<Parameters<PathGenerator>>) => ReturnType<PathGenerator>;

type SelectionGenerator = ReturnType<
  InstanceType<typeof InternalModuleFile>["generate_selection"]
>;
type Selection = (
  ...args: Partial<Parameters<SelectionGenerator>>
) => ReturnType<SelectionGenerator>;

type PromptGenerator = ReturnType<
  InstanceType<typeof InternalModuleSystem>["generate_prompt"]
>;

type ClipboardGenerator = ReturnType<
  InstanceType<typeof InternalModuleSystem>["generate_clipboard"]
>;
type Clipboard = (
  ...args: Partial<Parameters<ClipboardGenerator>>
) => ReturnType<ClipboardGenerator>;

type Prompt = (
  ...args: Partial<Parameters<PromptGenerator>>
) => ReturnType<PromptGenerator>;

type SuggesterGenerator = ReturnType<
  InstanceType<typeof InternalModuleSystem>["generate_suggester"]
>;
type Suggester = (
  ...args: Partial<Parameters<SuggesterGenerator>>
) => ReturnType<SuggesterGenerator>;
