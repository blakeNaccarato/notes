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
      selection: () => string;
    };
    system: {
      prompt: (prompt_text: string) => Promise<string | null>;
    };
  };
}
