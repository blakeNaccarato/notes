import type { InternalModuleFile } from "templater-obsidian/dist/core/functions/internal_functions/file/InternalModuleFile";
import type { InternalModuleSystem } from "templater-obsidian/dist/core/functions/internal_functions/system/InternalModuleSystem";

/**
 * Templater interface.
 */
export interface Templater {
  current_functions_object: {
    user: {
      cite: () => Promise<string>;
      getSelOrClip: () => Promise<string>;
      getTimeTrackingEntry: () => Promise<void>;
    };
    file: {
      selection: Selection;
    };
    system: {
      clipboard: Clipboard;
      prompt: Prompt;
      suggester: Suggester;
    };
  };
}

type SelectionGenerator = ReturnType<
  InstanceType<typeof InternalModuleFile>["generate_selection"]
>;
type Selection = (
  ...args: Partial<Parameters<SelectionGenerator>>
) => ReturnType<SelectionGenerator>;

type PromptGenerator = ReturnType<
  InstanceType<typeof InternalModuleSystem>["generate_prompt"]
>;
type Prompt = (
  ...args: Partial<Parameters<PromptGenerator>>
) => ReturnType<PromptGenerator>;

type ClipboardGenerator = ReturnType<
  InstanceType<typeof InternalModuleSystem>["generate_clipboard"]
>;
type Clipboard = (
  ...args: Partial<Parameters<ClipboardGenerator>>
) => ReturnType<ClipboardGenerator>;

type SuggesterGenerator = ReturnType<
  InstanceType<typeof InternalModuleSystem>["generate_suggester"]
>;
type Suggester = (
  ...args: Partial<Parameters<SuggesterGenerator>>
) => ReturnType<SuggesterGenerator>;
