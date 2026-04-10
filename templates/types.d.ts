import type { Moment } from "moment";
import type { App as RawApp } from "obsidian";
import type { DataviewApi } from "obsidian-dataview/lib/api/plugin-api";
import type { SMarkdownPage } from "obsidian-dataview/lib/data-model/serialized/markdown";
import type { InternalModuleFile } from "templater-obsidian/dist/core/functions/internal_functions/file/InternalModuleFile";
import type { InternalModuleSystem } from "templater-obsidian/dist/core/functions/internal_functions/system/InternalModuleSystem";

export type App = RawApp & {
  plugins: {
    getPlugin(id: "dataview"): {
      api: {
        page(...args: Parameters<DataviewApi["page"]>): SMarkdownPage | undefined;
      };
    };
    getPlugin(id: "templater-obsidian"): {
      templater: {
        current_functions_object: {
          file: {
            content: Awaited<
              (...args: Partial<Parameters<GenContent>>) => ReturnType<GenContent>
            >;
            path: (...args: Partial<Parameters<GenPath>>) => ReturnType<GenPath>;
            selection: (
              ...args: Partial<Parameters<GenSelection>>
            ) => ReturnType<GenSelection>;
          };
          obsidian: {
            moment: () => Moment;
          };
          system: {
            clipboard: (
              ...args: Partial<Parameters<GenClipboard>>
            ) => ReturnType<GenClipboard>;
            prompt: (...args: Partial<Parameters<GenPrompt>>) => ReturnType<GenPrompt>;
            suggester: (
              ...args: Partial<Parameters<GenSuggester>>
            ) => ReturnType<GenSuggester>;
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
      };
    };
  };
};

type GenContent = ReturnType<
  InstanceType<typeof InternalModuleFile>["generate_content"]
>;
type GenPath = ReturnType<InstanceType<typeof InternalModuleFile>["generate_path"]>;
type GenSelection = ReturnType<
  InstanceType<typeof InternalModuleFile>["generate_selection"]
>;
type GenPrompt = ReturnType<
  InstanceType<typeof InternalModuleSystem>["generate_prompt"]
>;
type GenClipboard = ReturnType<
  InstanceType<typeof InternalModuleSystem>["generate_clipboard"]
>;
type GenSuggester = ReturnType<
  InstanceType<typeof InternalModuleSystem>["generate_suggester"]
>;
