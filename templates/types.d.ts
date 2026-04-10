export type { default as TemplaterPlugin } from "templater-obsidian";
import type { Moment } from "moment";
import type { App as RawApp } from "obsidian";
import type { DataviewApi } from "obsidian-dataview/lib/api/plugin-api";
import type { SMarkdownPage } from "obsidian-dataview/lib/data-model/serialized/markdown";
import type { InternalModuleFile } from "templater-obsidian/dist/core/functions/internal_functions/file/InternalModuleFile";
import type { InternalModuleSystem } from "templater-obsidian/dist/core/functions/internal_functions/system/InternalModuleSystem";

/**
 * Templater interface.
 */
export interface Templater {
  current_functions_object: {
    app: App;
    file: {
      content: Content;
      path: Path;
      selection: Selection;
    };
    obsidian: {
      moment: () => Moment;
    };
    system: {
      clipboard: Clipboard;
      prompt: Prompt;
      suggester: Suggester;
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
  };
}

type App = RawApp & {
  plugins: Omit<RawApp["plugins"], "getPlugin"> & {
    getPlugin(id: "dataview"): DataviewPlugin;
  };
};

interface DataviewPlugin {
  api: Dataview;
}
interface Dataview {
  page(...args: Parameters<DataviewApi["page"]>): SMarkdownPage | undefined;
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
