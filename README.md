# notes

Centralized repository of my Obsidian vaults and shared tooling.

## Update common

Update files common to all vaults. Includes environment variables files, automation scripts, VSCode settings, and plugin patches. The text expander plugin needs [this patch](https://github.com/mrjackphil/obsidian-text-expand/issues/78). I will eventually open a PR to patch upstream. [This line](https://github.com/mrjackphil/obsidian-text-expand/blob/d896e5aff557b37daa566c55c147a6b81fee5717/src/sequences/sequences.ts#L276) is changed to the following in order to fix the `$searchresult` sequence:

```JavaScript
return results.vChildren.children.map(matchedFile => {
```
