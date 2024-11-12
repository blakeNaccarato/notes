# notes

Hello again

[![All Contributors](https://img.shields.io/github/all-contributors/blakeNaccarato/notes?color=ee8449&style=flat-square)](#contributors)

Centralized repository of my Obsidian vaults and shared tooling.

## Update common

Update files common to all vaults. Includes environment variables files, automation scripts, VSCode settings, and plugin patches. The text expander plugin needs [this patch](https://github.com/mrjackphil/obsidian-text-expand/issues/78). I will eventually open a PR to patch upstream. [This line](https://github.com/mrjackphil/obsidian-text-expand/blob/d896e5aff557b37daa566c55c147a6b81fee5717/src/sequences/sequences.ts#L276) is changed to the following in order to fix the `$searchresult` sequence:

```JavaScript
return results.vChildren.children.map(matchedFile => {
```

## Project information

- [Changes](<https://blakeNaccarato.github.io/notes/changelog.html>)
- [Docs](<https://blakeNaccarato.github.io/notes>)
- [Contributing](<https://blakeNaccarato.github.io/notes/contributing.html>)

## Project information

- [Changes](<https://blakeNaccarato.github.io/notes/changelog.html>)
- [Docs](<https://blakeNaccarato.github.io/notes>)
- [Contributing](<https://blakeNaccarato.github.io/notes/contributing.html>)

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://www.blakenaccarato.com/"><img src="https://avatars.githubusercontent.com/u/20692450?v=4?s=100" width="100px;" alt="Blake Naccarato"/><br /><sub><b>Blake Naccarato</b></sub></a><br /><a href="#code-blakeNaccarato" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
