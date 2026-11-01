# Claude Code repository registration

RPM packaging for `claude-code-repo`, a Lyra-authored package that registers
Anthropic's official Claude Code Zypper repository
(`downloads.claude.ai/claude-code/rpm/stable`) so `zypper install claude-code` resolves against
it.

Like [`vscode`](https://github.com/lyra-os-linux/vscode), this package
carries no upstream binary and no `_service`. The difference is the key:
Anthropic's repository is signed (`repomd.xml.asc`) but does not publish
`repomd.xml.key`, and no distribution package ships Anthropic's key. So
`claude-code-repo` ships it at `/usr/share/claude-code-repo/claude-code.asc` and points
`gpgkey=` at that file. The user still approves the key the first time, in
Vega (Software → Desenvolvedores → Claude Code) or when Zypper asks.

- `claude-code.repo`: the Zypper repository definition, with metadata and
  package GPG verification both enabled and third-party priority `90`;
- `claude-code.asc`: the Claude Code release signing key,
  `31DD DE24 DDFA B679 F42D 7BD2 BAA9 29FF 1A7E CACE`, from
  `https://downloads.claude.ai/keys/claude-code.asc`;
- `claude-code-repo.spec`: installs both files, and at build time asserts the
  repository settings and the key fingerprint;
- `claude-code-repo.changes`: RPM changelog.

## Atualizar a chave

Se a Anthropic trocar a chave, baixe a nova de
`https://downloads.claude.ai/keys/claude-code.asc`, confira que ela verifica
`repodata/repomd.xml.asc` do repositório e atualize a impressão digital no
`.spec`, nos testes e neste README.

## Validação

Em cada push para `main` e pull request, o CI executa:

```sh
python3 -m unittest discover -s tests -v
rpmspec -P claude-code-repo.spec >/dev/null
```

Os testes verificam a URL HTTPS oficial, a chave esperada (pela impressão
digital), `gpgcheck`, `repo_gpgcheck`, prioridade e instalação/remoção
idempotentes do arquivo.

## Credits

Claude Code is developed by [Anthropic](https://www.anthropic.com/). This package is not
affiliated with or endorsed by Anthropic; it only points Zypper at their
existing, official repository.
