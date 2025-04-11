// @ts-check

import { globalIgnores } from "eslint/config";
import tseslint from "typescript-eslint";

export default tseslint.config(
  tseslint.configs.strict,
  tseslint.configs.stylistic,
  [globalIgnores(["packages/templater-obsidian/*"])],
);
