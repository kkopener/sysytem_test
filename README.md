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

CSVアップロードにより一括更新を行う．

管理項目

* 基本シフト
* 経験者フラグ
* 未成年フラグ
* 所属店舗

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
* 未提出者は基本シフトを適用

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

| 項目     |
| ------ |
| 店舗コード  |
| 従業員ID  |
| パスワード  |
| 氏名     |
| 役割     |
| 経験者フラグ |
| 未成年フラグ |
| 曜日     |
| 勤務開始時刻 |
| 勤務終了時刻 |

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

本システムは以下の環境で開発を行う．

### 使用言語

* Python 3.12

### 使用フレームワーク

* Streamlit

### 使用ライブラリ

* Pandas
* NumPy（必要に応じて）
* Datetime

### 開発ツール

* Anaconda
* Visual Studio Code
* GitHub

---

## 開発環境構築

Anaconda上で本プロジェクト用の環境を作成し，必要なライブラリをインストールした．

今回は開発効率を優先し，Anaconda環境内へ必要なライブラリをまとめて導入する構成とした．

環境構築後，Visual Studio Codeからプロジェクトフォルダを開き，開発を行う．

---

## 起動方法

### ライブラリのインストール

VScode上のコマンドシェルにて以下のコマンドを入力した

```bash
pip install streamlit pandas
```

### アプリケーション起動

コマンドプロンプトを起動し，以下のコマンドを入力してアプリを起動した

```bash
streamlit run C:\　Users\　ユーザ名\　OneDrive\　ファイル保存フォルダ\　autoshift.py [ARGUMENTS]
```

### 動作確認

以下のテストプログラムを作成し，ブラウザ上で画面表示されることを確認した．

```python
import streamlit as st

st.title("シフト自動調整管理アプリ")
st.write("開発環境の動作確認")
```

実行後，ブラウザ上にタイトルおよびメッセージが表示されることを確認した．

---

## GitHubリポジトリ
```text
github
└─system_test/
    ├── app.py                  # メインエントリポイント（セッション初期化、画面ルーティングを統括）
    ├── config.py               # クラウドDB接続設定、環境変数（st.secrets）の管理
    ├── requirements.txt        # 依存ライブラリの定義（streamlit, pandas, supabase または firebase-admin等）
    ├── database/
    │   └── storage.py          # データアクセス層（ローカルCSVの代わりにクラウドDBのCRUD処理を実装）
    ├── services/
    │   ├── employee_service.py # 従業員管理ビジネスロジック（バリデーションや削除時の安全ロック）
    │   ├── holiday_service.py  # 休み希望に関するロジック
    │   └── roster_service.py   # シフト自動生成アルゴリズム・人手不足（タイムカバー）チェック
    └── views/                  # 画面・UI表示層（旧関数の表示・入力ロジックをそのまま移設）
        ├── auth_view.py        # ログイン画面 ＆ 新規店舗・部門設立画面のUI
        ├── admin_view.py       # 管理者ダッシュボードのUI（各タブの表示含む）
        └── employee_view.py    # 一般従業員ダッシュボードのUI

```

現段階ではプロジェクト初期段階であり、
システム本体およびCSVデータは今後実装予定である。
現在は開発環境構築および要件定義・設計の段階である。

