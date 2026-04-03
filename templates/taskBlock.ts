/**
 * Obsidian Tasks block
 *
 * @param contents Contents of the task block
 */
export default (text: string): string => `\`\`\`tasks${text}
\`\`\``;
