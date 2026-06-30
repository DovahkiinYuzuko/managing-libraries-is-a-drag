# Managing Libraries is a Drag

外部ライブラリ追加時のドキュメント更新を自動化するAIエージェント用スキル / An AI agent skill that automates document updates when adding external libraries.

![License](https://img.shields.io/badge/license-MIT-yellow?style=flat-square&logoColor=white)
![Python](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square&logo=python)

[日本語](#日本語) | [English](#english)

## 日本語

### 概要
本スキルは、プロジェクトに外部ライブラリが追加された際、その情報の取得およびライブラリ倉庫（`docs/using-library/lib-WH.md`）の更新を自動化するためのAIエージェント用スキルです。

### 導入のメリット
- **ライセンス管理の効率化:** 外部ライブラリの情報が1つのファイル（`lib-WH.md`）に集約されるため、後からサードパーティライセンスの表記を行う際に、各パッケージマネージャーの設定ファイルを巡回して調査する手間を削減できます。
- **採用経緯の可視化:** 導入時に「説明」と「採用理由」の記述を必須とすることで、「なぜこのライブラリが導入されたのか」が後からいつでも確認可能になり、依存関係のブラックボックス化や形骸化を防ぎます。

### 機能
- **自動情報ルックアップ:** `deps.dev API` を利用し、対応エコシステム（npm, cargo, pypi, go, rubygems, maven, nuget）のライセンスおよびデフォルトバージョンを自動で取得します。
- **フォールバックハンドリング:** API非対応のシステム、または情報取得失敗時において、エージェントがWeb検索や自身の知識を用いて自動で情報を補完します。
- **安全設計:** 実行される Python スクリプトはAPIからのデータ取得（JSON出力）のみを行い、ローカルファイルの書き換えや削除などの破壊的変更を一切行いません。ファイルの更新はエージェント自身のファイル操作能力によって行われます。

### インストール方法
本スキルは、オープンエージェントスキルエコシステムのパッケージマネージャーである `npx skills` を使用してインストールできます。

```bash
npx skills add DovahkiinYuzuko/managing-libraries-is-a-drag
```

### 使用方法
エージェントに対し、新規ライブラリを追加した旨を指示します。

**実行フロー:**
1. エージェントが対象コードやコンテキストから、該当ライブラリの `Description`（説明）と `Rationale`（採用理由）の候補を自律的に下書きし、ユーザーに確認を求めます。
2. ユーザーの承認を受けた後、エージェントが情報取得スクリプト（`scripts/fetch-lib-info.py`）を実行します。
3. 取得した情報（バージョン、ライセンス）を基に、`docs/using-library/lib-WH.md` の該当する言語セクションへ、アルファベット順になるよう自動で追記・更新を行います。

### LICENSE
このプロジェクトのライセンスはMITです。詳しくは[LICENSE](LICENSE)をお読みください。

---

## English

### Overview
This skill is an AI agent skill designed to automate data retrieval and updating of the central library warehouse (`docs/using-library/lib-WH.md`) when a new external library is added to a project.

### Benefits
- **Efficient License Management:** By centralizing external library information into a single file (`lib-WH.md`), it eliminates the need to search through various package manager configuration files when compiling third-party license notices later.
- **Traceability of Dependency Context:** Requiring a "Description" and "Rationale" upon installation ensures that the context behind why a library was introduced remains clear, preventing dependencies from becoming a black box or obsolete over time.

### Features
- **Automated Information Lookup:** Automatically retrieves the license and default version for supported ecosystems (npm, cargo, pypi, go, rubygems, maven, nuget) utilizing the `deps.dev API`.
- **Fallback Handling:** For unsupported ecosystems or when data retrieval fails, the agent autonomously complements the information using web search or its own knowledge.
- **Safe Design:** The executed Python script only performs data retrieval from the API (JSON output) and does not make any destructive changes such as rewriting or deleting local files. File updates are handled via the agent's file manipulation capabilities.

### Installation
This skill can be installed using `npx skills`, the package manager for the open agent skill ecosystem.

```bash
npx npx skills add DovahkiinYuzuko/managing-libraries-is-a-drag
```

### Usage
Instruct the agent that a new library has been added.

**Execution Flow:**
1. The agent autonomously drafts the `Description` and `Rationale` for the library based on the target code or context and requests user confirmation.
2. Upon receiving user approval, the agent executes the information retrieval script (`scripts/fetch-lib-info.py`).
3. Based on the retrieved information (version, license), the agent automatically appends or updates the entry under the correct language section in `docs/using-library/lib-WH.md` in alphabetical order.

### LICENSE
The license for this project is MIT. See [LICENSE](LICENSE) for details.