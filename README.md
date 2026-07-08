# sysytem_test

# シフト自動調整管理アプリ 要件定義書

## 1. プロジェクト概要

### システム名

簡易複数店舗対応型・シフト自動調整管理アプリ

### 開発期間

4週間

### 概要

複数店舗・部門に対応し，従業員の基本シフトと月次の休み希望を組み合わせて，スキルバランスや法令上の制約を考慮した月間シフト表を自動生成・管理するWebアプリケーションである．

### 使用技術

* Python
* Streamlit
* Streamlit Community Cloud
* CSVファイル管理

---

## 2. システム目的

本システムは，複数店舗におけるシフト作成業務を効率化することを目的とする．

以下の3ステップでシフトを作成する．

1. 基本シフトの自動配置
2. 希望休の反映
3. ルールベースの自動穴埋め

これにより管理者のシフト作成負担を軽減する．

---

## 3. システム構成

```mermaid
flowchart TD

A[従業員マスタ CSV]
B[休み希望入力]
C[シフト自動生成エンジン]
D[管理者修正画面]
E[確定シフト]
F[CSVダウンロード]
G[従業員閲覧画面]

A --> C
B --> C
C --> D
D --> E
E --> G
E --> F
```

---

## 4. ユーザー区分

| 区分    | 利用機能               |
| ----- | ------------------ |
| 一般従業員 | 希望休提出，確定シフト閲覧      |
| 管理者   | 従業員管理，自動生成，手動修正，公開 |

---

## 5. 機能要件

### 共通機能

#### FR-01 簡易ログイン

* 店舗コード
* 従業員ID
* パスワード

を用いて認証を行う．

ユーザー権限に応じて画面を分岐する．

---

### 一般従業員機能

#### FR-02 希望休提出

* 日単位で休み希望を登録
* 備考入力可能
* 保存可能

#### FR-03 確定シフト閲覧

* 管理者公開後に閲覧可能
* 月間シフトを確認可能

---

### 管理者機能

#### FR-04 従業員マスタ管理

管理者画面のUIフォームから従業員の追加・契約解除（削除）を行う．
また，登録時に曜日や日数の矛盾チェックを実施し，データ整合性を担保する．

管理項目
* 基本情報（従業員ID，パスワード，氏名，役割）
* シフト条件（通常出勤曜日・時間，追加可能曜日・時間，絶対NG曜日）
* 制限設定（週最大出勤日数，週制限超過許可）
* 経験者フラグ
* 未成年フラグ

#### FR-05 提出状況確認

各従業員の提出状況を表示する．

* 提出済
* 未提出

#### FR-06 シフト自動生成

以下のルールを適用する．

1. 基本シフトを配置
2. 希望休を反映
3. 空き枠を自動補完

##### 制約条件

* 各時間帯に経験者を1名以上配置
* 未成年者は22時以降勤務不可
* 絶対NG曜日に指定された日は割り当てない
* 各従業員の「週最大出勤日数」を超過しない（超過許可フラグONの場合は除く）

#### FR-07 シフト手動修正

* セル単位編集
* ドロップダウン選択
* 即時保存

#### FR-08 労働時間集計

従業員ごとの総勤務時間を自動計算する．

#### FR-09 シフト公開

公開ボタン押下後に従業員へ反映する．

#### FR-10 CSV出力

完成したシフト表をCSV形式でダウンロードする．

---

## 6. 非機能要件

### 性能

* ログイン：5秒以内
* 画面遷移：5秒以内
* 自動生成処理：5秒以内

### セキュリティ

* 権限制御を実施
* パスワード暗号化は行わない

### ユーザビリティ

* Streamlit標準UIを利用
* 表形式編集を採用

### 保守性

* SQLは使用しない
* CSVファイル管理とする
* 手動修復可能なデータ構造とする

---

## 7. データ構造

### employees.csv

| 項目 |
| --- |
| 店舗コード |
| 従業員ID |
| パスワード |
| 氏名 |
| 役割 |
| 通常出勤曜日 |
| 通常開始時刻 |
| 通常終了時刻 |
| 追加可能曜日 |
| 追加可能開始時刻 |
| 追加可能終了時刻 |
| 絶対NG曜日 |
| 週最大出勤日数 |
| 週制限超過許可 |
| 経験者フラグ |
| 未成年フラグ |

### shifts_YYYY_MM.csv

| 項目    |
| ----- |
| 日付    |
| 店舗コード |
| 時間    |
| シフト枠1 |
| シフト枠2 |
| 備考    |

---

## 8. 非目標

以下の機能は開発対象外とする．

* ユーザー新規登録
* パスワード再発行
* 時間単位の休暇申請
* 勤務時間超過アラート
* 給与計算
* 他システム連携
* LINE通知
* メール通知
* PDF出力
* 高度なセキュリティ機能

---

## 9. 開発優先度

| 優先度 | 対象機能                      |
| --- | ------------------------- |
| 高   | ログイン，休み希望，自動生成，マスタ管理，手動修正 |
| 中   | 提出状況確認，公開機能，労働時間集計        |
| 低   | なし                        |


# システム構成図

## 1. ユースケース図

```mermaid

graph LR
    %% アクターの定義
    subgraph Actors [アクター]
        Emp((一般従業員))
        Admin((管理者))
    end

    %% ユースケースの定義
    subgraph UseCases [ユースケース]
        %% 共通
        UC_Login((1. 簡易ログイン))
        UC_View((7. 確定シフト閲覧))

        %% 従業員用
        UC_Submit((3. シフト希望提出))

        %% 管理者用
        UC_Masta((2. 従業員マスタ更新<br>Excelアップロード))
        UC_Visual((4. 提出状況の可視化))
        UC_Auto((5. 穴埋め式シフト自動調整))
        UC_Manual((6. 欠員対応・手動修正))
        UC_Aggregate((6. 勤務時間自動集計))
        UC_Publish((7. 確定・公開制御))
        UC_Download((7. CSVダウンロード<br>バックアップ))
    end

    %% 関係性の定義 (アクター -> ユースケース)
    Emp --> UC_Login
    Admin --> UC_Login

    Emp --> UC_Submit
    Emp --> UC_View

    Admin --> UC_Masta
    Admin --> UC_Visual
    Admin --> UC_Auto
    Admin --> UC_Manual
    Admin --> UC_Publish

    %% 関連ユースケースの関係性 (include / extend 相当)
    UC_Submit -. "include (CSV上書き保存)" .-> UC_Submit
    UC_Masta -. "include (CSV上書き保存)" .-> UC_Masta
    
    UC_Auto -. "include (基本シフト・希望休反映)" .-> UC_Manual
    UC_Manual -. "include (リアルタイム計算)" .-> UC_Aggregate
    UC_Manual -. "include (CSV上書き保存)" .-> UC_Manual
    
    UC_Publish -. "extend (従業員画面へ開示)" .-> UC_View
    UC_Publish -. "extend (ローカル保存)" .-> UC_Download

    %% スタイルの調整
    style Emp fill:#f9f,stroke:#333,stroke-width:2px
    style Admin fill:#bbf,stroke:#333,stroke-width:2px
```



## 2. クラス図

```mermaid
classDiagram
    class Shop {
        +String shopCode
        +String shopName
    }

    class User {
        <<Abstract>>
        +String empId
        +String password
        +String name
        +String role
        +login(String password) Boolean
    }

    class Employee {
        +String ability
        +Boolean isMinor
        +BaseShift baseShift
        +submitRequest(List~String~ dates, String memo)
    }

    class Admin {
        +uploadEmployeeMasta(String csvFile)
        +runAutoAdjustment(String month)
        +updateShiftManually(ShiftTable table)
        +publishShift(String month)
    }

    class BaseShift {
        +String dayOfWeek
        +List~int~ availableHours
    }

    class ShiftTable {
        +String month
        +Boolean isPublished
        +calculateTotalHours(String empId) int
    }

    class ShiftRow {
        +String date
        +int hour
        +String assignedEmpId
        +String memo
    }

    class CSVManager {
        +loadEmployees(String shopCode) List~Employee~
        +saveEmployees(String shopCode, List~Employee~ employees)
        +loadShiftTable(String shopCode, String month) ShiftTable
        +saveShiftTable(String shopCode, ShiftTable table)
    }

    %% 継承関係 (Inheritance)
    User <|-- Employee
    User <|-- Admin

    %% コンポジション関係 (Composition) - ライフサイクルが同一
    Employee "1" *-- "7" BaseShift : 曜日ごとに保持
    ShiftTable "1" *-- "*" ShiftRow : 1時間単位の行

    %% 集約関係 (Aggregation) - 所属・管理の関係
    Shop "1" o-- "*" User : 所属する
    Shop "1" o-- "*" ShiftTable : 該当店舗の月次シフト

    %% 関連 (Association) - 操作・利用の関係
    Admin ..> CSVManager : CSVアップロード/保存で利用
    ShiftTable ..> CSVManager : データの読み書きで利用
```

## 3. シーケンス図

### 3.1. 従業員のシフト提出
```mermaid
sequenceDiagram
    autonumber
    actor Emp as 一般従業員 (Actor)
    participant UI as 従業員画面 (UI)
    participant Ctrl as シフトコントローラ (Controller)
        participant Model as CSVマネージャ (Model/DB)

    Emp ->> UI: ログイン後、希望提出画面を開く
    activate UI
    UI ->> Ctrl: 希望受付ステータス確認要請
    Ctrl ->> Model: 該当月のシフトファイル状態を取得
    Model -->> Ctrl: ファイル情報（公開前/受付中）
    Ctrl -->> UI: 提出フォームを表示
    deactivate UI

    %% 休み希望の選択と送信
    Emp ->> UI: 休み希望日(複数)を選択、備考を入力して「提出」
    activate UI
    UI ->> Ctrl: 希望データ送信(Dates[], Memo)
    activate Ctrl
    
    %% 条件分岐: 提出期限・権限チェック
    alt 提出期限内 かつ 認証有効
        
        %% ループ処理: 選択された日付ごとにCSVへ書き込み準備
        loop 選択された各日付 (date in Dates[])
            Ctrl ->> Model: 休み希望の書き込み指示(empId, date, "希望休", memo)
            activate Model
            Model ->> Model: CSVファイル内該当セルを「OFF」に上書き
            Model -->> Ctrl: 書き込み完了
            deactivate Model
        end
        
        Ctrl -->> UI: 提出成功メッセージを返す
    else 期限切れ または セッション無効
        Ctrl -->> UI: エラーメッセージを返す（「提出を締め切りました」等）
    end
    deactivate Ctrl
    UI -->> Emp: 画面に処理結果を表示
    deactivate UI
```

### 3.2. 管理者によるシフトの自動調整および手動調整
```mermaid
sequenceDiagram
    autonumber
    actor Admin as 管理者 (Actor)
    participant UI as 管理者画面 (UI)
    participant Ctrl as 自動生成エンジン (Controller)
    participant Model as CSVマネージャ (Model/DB)

    %% 自動生成の実行
    Admin ->> UI: 「シフト自動調整」ボタンを押す
    activate UI
    UI ->> Ctrl: 自動生成リクエスト(店舗コード, 対象月)
    activate Ctrl
    
    Ctrl ->> Model: 従業員マスタ ＆ 休み希望CSVを読み込み
    activate Model
    Model -->> Ctrl: 従業員データ、提出済みの希望データ
    deactivate Model

    Ctrl ->> Ctrl: 【STEP1】基本シフトをベースに全日程へ仮配置
    Ctrl ->> Ctrl: 【STEP2】提出された「希望休」の枠を空席(穴)にする

    %% ループと条件分岐: 1日1時間ごとの穴埋めとルールチェック
    loop 1ヶ月間のすべての「日」 × 「1時間単位の時間枠」
        Ctrl ->> Ctrl: 空席枠に対し、出勤可能な他メンバーを探索
        
        alt 候補者が「未成年」かつ「22時以降」
            Ctrl ->> Ctrl: 割り当てをスキップ (不適合)
        else 候補者の中に「経験者」が含まれる
            Ctrl ->> Ctrl: スキルバランス良好として枠に割り当て
        else 経験者がいない場合
            Ctrl ->> Ctrl: 警告フラグ付きで割り当て、または空席のままにする
        end
    end

    Ctrl ->> Model: 一時生成されたシフトデータを保存
    Ctrl -->> UI: 自動生成結果のシフト表を表示（未充足パターンの可視化）
    deactivate Ctrl
    UI -->> Admin: 画面に自動生成結果（Excel風テーブル）を提示
    deactivate UI

    %% 管理者による手動修正（機能6）
    Admin ->> UI: 空席やバランスの悪いセルを手動で修正し「確定保存」
    activate UI
    UI ->> Ctrl: 手動修正データ送信(UpdatedTable)
    activate Ctrl
    Ctrl ->> Ctrl: 従業員ごとの勤務合計時間をリアルタイム再計算
    Ctrl ->> Model: 最終確定したシフトデータをCSVに上書き保存
    activate Model
    Model -->> Ctrl: 保存完了通知
    deactivate Model
    Ctrl -->> UI: 更新成功 ＆ 合計勤務時間を画面に反映
    deactivate Ctrl
    UI -->> Admin: 「変更を保存しました」と合計時間を画面に表示
    deactivate UI
```

## 4. 状態遷移図
```mermaid
stateDiagram-v2
    [*] --> 未作成 : 月が替わる / 管理者が新しい月を指定

    未作成 --> 希望受付中 : トリガー: 管理者が「翌月のシフト作成」を開始<br>(CSVファイルの初期生成)
    
    state 希望受付中 {
        [*] --> 未提出
        未提出 --> 提出済 : トリガー: 一般従業員が「希望休」を送信
        提出済 --> 提出済 : トリガー: 締切前なら再修正・再提出が可能
    }

    希望受付中 --> 自動生成済み : トリガー: 提出期限到来後、管理者が「自動調整」ボタンを押下<br>(基本シフト割当・希望休の穴あけ・ルール準拠の穴埋めを実行)

    自動生成済み --> 調整中 : トリガー: 管理者が画面上で手動修正を開始

    調整中 --> 調整中 : トリガー: セルを編集し「一時保存」を押下<br>(勤務合計時間のリアルタイム再計算)

    調整中 --> 確定・公開済み : トリガー: 管理者が最終確認し「公開」ボタンを押下<br>(従業員画面へ開示・ロック)
    自動生成済み --> 確定・公開済み : トリガー: 自動生成の結果が完璧で、そのまま「公開」ボタンを押下

    state 確定・公開済み {
        [*] --> 運用中
        運用中 --> 急な欠員発生 : トリガー: 従業員から欠勤連絡
        急な欠員発生 --> 運用中 : トリガー: 管理者が代替者を画面上で手動差し替え(上書き保存)
    }

    確定・公開済み --> バックアップ完了 : トリガー: 管理者が「CSVダウンロード」を実行<br>(ローカルPCへ保存)

    バックアップ完了 --> [*] : 月の終了 (運用の終了)
```

# 開発環境およびGitHubリポジトリ

## 開発環境

本システムは以下の環境で開発および動作確認を行っている．

### OS
* Windows 10 / Windows 11

### 使用言語
* Python 3.12以上

### 使用フレームワーク
* Streamlit

### 使用ライブラリ
* streamlit
* pandas
* numpy
* openpyxl
* その他 `requirements.txt` に記載されたライブラリ

### 開発ツール
* Visual Studio Code
* GitHub
* GitHub Desktop

---

## 開発環境構築

本プロジェクトは，Windows標準のPython環境と付属のバッチファイルを用いて，容易に環境構築が可能な構成となっている．
Anaconda環境は不要である．

### 1. 事前準備：Pythonのインストール
本システムを動作させるためには，PCにPythonがインストールされており，コマンドプロンプトから呼び出せる状態（PATHが通っている状態）である必要がある．
Pythonが未インストールの場合は，以下の手順で導入する．

1. [Python公式サイト](https://www.python.org/downloads/)にアクセスし，Windows用のインストーラ（Python 3.11 または 3.12 推奨）をダウンロードする．
2. ダウンロードしたインストーラ（`.exe`ファイル）を起動する．
3. **【最重要】** 最初のインストール画面の下部にある **「Add python.exe to PATH」** （または「Add Python 3.x to PATH」）のチェックボックスに**必ずチェックを入れる**．
   ※このチェックを忘れると，後述の自動セットアップが失敗するため注意すること．
4. 「Install Now」をクリックし，インストールを完了させる．

### 2. 環境セットアップ
Pythonの準備が完了したら，以下の手順でプロジェクトの環境を構築する．

1. 本リポジトリをダウンロード，またはGitHub Desktop等を用いてCloneする．
2. プロジェクトフォルダ（`sysytem_test/source`）内にある `setup.bat` をダブルクリックして実行する．

`setup.bat` を実行すると，以下の処理が自動で行われる．
* Pythonインストール状況およびPATHの確認
* プロジェクト専用の仮想環境（`.venv`）の作成
* `pip` の最新化
* `requirements.txt` に定義された必要ライブラリ（Streamlit, Pandas等）の自動インストール

---

## 起動方法

環境構築完了後，以下の手順でアプリケーションを起動する．

1. 初回のみ，前述の通り `setup.bat` を実行し環境を構築する．
2. プロジェクトフォルダ内にある `run.bat` をダブルクリックして実行する．
3. 自動的に仮想環境が有効化され，Streamlitサーバーが起動する．その後，既定のWebブラウザが自動的に開き，アプリケーションの画面が表示される．

---

## 動作確認

`run.bat` 実行後，Webブラウザ上で本アプリのログイン画面（または新規店舗設立画面）が表示されれば，正常にセットアップおよび起動が完了している．

## GitHubリポジトリ
```text
プロジェクト構成は以下を基本とする。

sysytem_test/source/
├── app.py                 # アプリケーションのメインエントリーポイント
├── config.py              # アプリ共通設定（ページタイトル等）
├── requirements.txt       # 依存ライブラリ定義ファイル
├── setup.bat              # 自動環境構築用バッチファイル
├── run.bat                # アプリ起動用バッチファイル
│
├── views/                 # UI・画面表示用モジュール
│   ├── auth_view.py       # ログイン・新規店舗設立画面
│   ├── admin_view.py      # 管理者用ダッシュボード（シフト生成・編集）
│   └── employee_view.py   # 従業員用ダッシュボード（シフト閲覧・希望休提出）
│
├── database/              # データベース・ファイル操作用モジュール
│   └── storage.py         # CSVファイルの安全な読み書きロジック
│
├── services/              # ビジネスロジック処理用モジュール
│   ├── shift_generator.py # シフト自動生成・充足度チェックエンジン
│   └── csv_manager.py     # 各種マスタ・設定・希望休・シフトの管理
│
├── models/                # データ構造定義モジュール
│   ├── employee.py        # 従業員データモデル
│   ├── shift.py           # シフトデータモデル
│   └── shop.py            # 店舗データモデル
│
├── utils/                 # 汎用ユーティリティ・ヘルパー
│   ├── validator.py       # 入力値やデータのバリデーション処理
│   └── helper.py          # その他共通関数
│
└── data/                  # 各種CSVデータの保存先ディレクトリ

```


