<div align="center">

  <img src="https://github.com/Gourieff/Assets/raw/main/sd-webui-reactor/ReActor_logo_NEW_EN.png?raw=true" alt="logo" width="180px"/>

  ![Version](https://img.shields.io/badge/node_version-0.5.2_beta1-green?style=for-the-badge&labelColor=darkgreen)

  <!--<sup>
  <font color=brightred>

  ## !!! [重要なアップデート](#latestupdate) !!!<br>既存のワークフローにノードを再度追加することを忘れないでください
  
  </font>
  </sup>-->
  
  <a href="https://boosty.to/artgourieff" target="_blank">
    <img src="https://lovemet.ru/img/boosty.jpg" width="108" alt="Support Me on Boosty"/>
    <br>
    <sup>
      Support This Project
    </sup>
  </a>

  <hr>
  
  [![Commit activity](https://img.shields.io/github/commit-activity/t/Gourieff/ComfyUI-ReActor/main?cacheSeconds=0)](https://github.com/Gourieff/ComfyUI-ReActor/commits/main)
  ![Last commit](https://img.shields.io/github/last-commit/Gourieff/ComfyUI-ReActor/main?cacheSeconds=0)
  [![Opened issues](https://img.shields.io/github/issues/Gourieff/ComfyUI-ReActor?color=red)](https://github.com/Gourieff/ComfyUI-ReActor/issues?cacheSeconds=0)
  [![Closed issues](https://img.shields.io/github/issues-closed/Gourieff/ComfyUI-ReActor?color=green&cacheSeconds=0)](https://github.com/Gourieff/ComfyUI-ReActor/issues?q=is%3Aissue+is%3Aclosed)
  ![License](https://img.shields.io/github/license/Gourieff/ComfyUI-ReActor)

  [English](/README.md)  | [Русский](/README_RU.md) | 日本語

# ReActor Node for ComfyUI

</div>

### ブロックされた[ReActor](https://github.com/Gourieff/comfyui-reactor-node)に基づく、ComfyUIのための高速でシンプルな顔交換拡張ノード - NSFW検出器付き

> このノードを使用することにより、あなたは[責任](#disclaimer)を理解することになります

<div align="center">

---
[**What's new**](#latestupdate) | [**Installation**](#installation) | [**Usage**](#usage) | [**Troubleshooting**](#troubleshooting) | [**Updating**](#updating) | [**Disclaimer**](#disclaimer) | [**Credits**](#credits) | [**Note!**](#note)

---

</div>

<a name="latestupdate">

## 最新の更新内容

### 0.5.2 <sub><sup>BETA1</sup></sub>

- ReSwapperモデルのサポート。Inswapperは依然として最高の類似性を持っていますが、ReSwapperは進化しています - ReSwapperモデルとReSwapperプロジェクトに感謝します！これは、Inswapperの代替作成においてコミュニティにとって良い一歩です！

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.5.2-whatsnew-03.jpg?raw=true" alt="0.5.2-whatsnew-03" width="100%"/>
<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.5.2-whatsnew-04.jpg?raw=true" alt="0.5.2-whatsnew-04" width="100%"/>

ReSwapperモデルは以下からダウンロードできます：
https://huggingface.co/datasets/Gourieff/ReActor/tree/main/models
それらを "models/reswapper" ディレクトリに保存してください。

### 0.5.2 <sub><sup>ALPHA3</sup></sub>

- NSFW検出器を追加して、[GitHubのルール](https://docs.github.com/en/site-policy/acceptable-use-policies/github-misinformation-and-disinformation#synthetic--manipulated-media-tools)に違反しないようにしました。

### 0.5.2 <sub><sup>ALPHA2</sup></sub>

- 小さな修正

### 0.5.2 <sub><sup>ALPHA1</sup></sub>

- 新しいノード "Unload ReActor Models" - 複雑なワークフローでReActorが使用するVRAMを解放するのに役立ちます

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.5.2-whatsnew-01.jpg?raw=true" alt="0.5.2-whatsnew-01" width="100%"/>

- ORT CoreMLおよびROCM EPのサポート、必要なonnxruntimeバージョンをインストールするだけです
- 最新バージョンのORT-GPUをインストールするためのインストールスクリプトの改善

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.5.2-whatsnew-02.jpg?raw=true" alt="0.5.2-whatsnew-02" width="50%"/>

<details>
	<summary><a>以前のバージョン</a></summary>

### 0.5.1

- GPEN 1024/2048復元モデルのサポート（HFデータセットで利用可能 https://huggingface.co/datasets/Gourieff/ReActor/tree/main/models/facerestore_models）
- ReActorFaceBoostノード - 交換された顔の品質を向上させる試み。アイデアは、交換された顔を復元し、ターゲット画像に貼り付ける前に（inswapperアルゴリズムを介して）スケ��リングすることです。詳細は[こちら（PR#321）](https://github.com/Gourieff/comfyui-reactor-node/pull/321)をご覧ください。

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.5.1-whatsnew-01.jpg?raw=true" alt="0.5.1-whatsnew-01" width="100%"/>

[フルサイズのデモプレビュー](https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.5.1-whatsnew-02.png)

- 顔モデルのアルファベット順ソート
- 多くの修正と改善

### [0.5.0 <sub><sup>BETA4</sup></sub>](https://github.com/Gourieff/comfyui-reactor-node/releases/tag/v0.5.0)

- GFPGANのSpandrelライブラリのサポート

### 0.5.0 <sub><sup>BETA3</sup></sub>

- MaskingHelperの "RAM issue"、"No detection" の修正

### 0.5.0 <sub><sup>BETA2</sup></sub>

- 既存の顔モデルのバッチからブレンドされた顔モデルを作成できるようになりました。ワークフローに "Make Face Model Batch" ノードを追加し、"Load Face Model" ノードを介して複数のモデルを接続します。
- 画像解析モジュールのパフォーマンスが大幅に向上しました！10倍のスピードアップ！ビデオの作業が楽しくなりました！

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.5.0-whatsnew-05.png?raw=true" alt="0.5.0-whatsnew-05" width="100%"/>

### 0.5.0 <sub><sup>BETA1</sup></sub>

- Masking HelperノードのSWAPPED_FACE出力
- Masking HelperのIMAGE出力の空のAチャンネル（いくつかのノードでエラーを引き起こす）が削除されました

### 0.5.0 <sub><sup>ALPHA1</sup></sub>

- ReActorBuildFaceModelノードに "face_model" 出力が追加され、ブレンドされた顔モデルを直接メインノードに提供できます：

基本的なワークフロー [💾](https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/workflows/ReActor--Build-Blended-Face-Model--v2.json)

- 顔マスキング機能が利用可能になりました。"ReActorMaskHelper" ノードをワークフローに追加し、以下のように接続します：

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.5.0-whatsnew-01.jpg?raw=true" alt="0.5.0-whatsnew-01" width="100%"/>

"face_yolov8m.pt" Ultralyticsモデルがない場合は、[Assets](https://huggingface.co/datasets/Gourieff/ReActor/blob/main/models/detection/bbox/face_yolov8m.pt)からダウンロードし、"ComfyUI\models\ultralytics\bbox" ディレクトリに保存してください。
<br>
"Sams" モデルも同様に、[こちら](https://huggingface.co/datasets/Gourieff/ReActor/tree/main/models/sams)からダウンロードし、"ComfyUI\models\sams" ディレクトリに保存してください。

このノードを使用して、顔交換プロセスの最良の結果を得ることができます：

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.5.0-whatsnew-02.jpg?raw=true" alt="0.5.0-whatsnew-02" width="100%"/>

- ReActorImageDublicatorノード - ビデオを作成する人にとって非常に便利で、1つの画像を複数のフレームに複製し、VAEエンコーダーと一緒に使用できます（例：ライブアバター）：

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.5.0-whatsnew-03.jpg?raw=true" alt="0.5.0-whatsnew-03" width="100%"/>

- ReActorFaceSwapOpt（メインノードの簡略版）+ ReActorOptionsノードを追加して、追加のオプションを設定できます（新しい）"input/source faces separate order"。はい！インデックス内の顔の順序を任意に設定できます（デフォルトでは "large to small" です）！

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.5.0-whatsnew-04.jpg?raw=true" alt="0.5.0-whatsnew-04" width="100%"/>

- ターゲット画像の解析速度が少し向上しました（残念ながら、交換や復元に比べてまだかなり遅いです...）

### [0.4.2](https://github.com/Gourieff/comfyui-reactor-node/releases/tag/v0.4.2)

- GPEN-BFR-512およびRestoreFormer_Plus_Plus顔復元モデルのサポート

モデルはここからダウンロードできます：https://huggingface.co/datasets/Gourieff/ReActor/tree/main/models/facerestore_models
<br>それらを `ComfyUI\models\facerestore_models` フォルダに保存してください

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.4.2-whatsnew-04.jpg?raw=true" alt="0.4.2-whatsnew-04" width="100%"/>

- 多くのリクエストに応じて、複数の画像から1つの顔モデルファイルにブレンドできるようになりました。"Load Face Model" ノードまたはSD WebUIで使用できます。

実験して新しい顔を作成したり、1人の顔をブレンドして精度と���似性を向上させたりできます！

ImpactPackの "Make Image Batch" ノードをReActorの入力として追加し、ブレンドしたい画像をロードします：

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.4.2-whatsnew-01.jpg?raw=true" alt="0.4.2-whatsnew-01" width="100%"/>

結果の例（異なる女優の4つの顔から新しい顔が作成されました）：

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.4.2-whatsnew-02.jpg?raw=true" alt="0.4.2-whatsnew-02" width="75%"/>

基本的なワークフロー [💾](https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/workflows/ReActor--Build-Blended-Face-Model--v1.json)

### [0.4.1](https://github.com/Gourieff/comfyui-reactor-node/releases/tag/v0.4.1)

- CUDA 12サポート - ComfyUIのPythonエンクロージャー用に（Windows）`install.bat`または（Linux/MacOS）`install.py`を実行するか、ORT-GPUを手動でインストールしてください（https://onnxruntime.ai/docs/install/#install-onnx-runtime-gpu-cuda-12x）
- Issue https://github.com/Gourieff/comfyui-reactor-node/issues/173 の修正

- 顔復元後処理のための別のノード（FR https://github.com/Gourieff/comfyui-reactor-node/issues/191）、ReActorのメニュー内にあります（RestoreFaceノード）
- （Windows）インストールはシステムのPATHからのPythonに対して実行できます
- さまざまな修正と改善

- 顔復元の可視性とCodeFormerの重み（忠実度）オプションが利用可能になりました！既存のワークフローでノードを再読み込みすることを忘れないでください

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.4.1-whatsnew-01.jpg?raw=true" alt="0.4.1-whatsnew-01" width="100%"/>

### [0.4.0](https://github.com/Gourieff/comfyui-reactor-node/releases/tag/v0.4.0)

- 入力 "input_image" が最初に来るようになり、正しいバイパスが可能になり、メイン入力が最初に来るのが正しいです。
- 顔モデルを "safetensors" ファイルとして保存し、ReActorにロードしてさまざまなシナリオを実装し、使用する顔の超軽量な顔モデルを保持できます：

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.4.0-whatsnew-01.jpg?raw=true" alt="0.4.0-whatsnew-01" width="100%"/>
<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.4.0-whatsnew-02.jpg?raw=true" alt="0.4.0-whatsnew-02" width="100%"/>

- 画像から直接顔モデルを作成して保存する機能：

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/0.4.0-whatsnew-03.jpg?raw=true" alt="0.4.0-whatsnew-03" width="50%"/>

- 両方の入力はオプションであり、ワークフローに応じて1つを接続します。両方が接続されている場合、`image` が優先されます。
- この拡張機能をより良くするためのさまざまな修正。

バグを見つけ、新機能を提案し、このプロジェクトをサポートしてくれるすべての人に感謝します！

</details>

## インストール

<details>
	<summary>SD WebUI: <a href="https://github.com/AUTOMATIC1111/stable-diffusion-webui/">AUTOMATIC1111</a> または <a href="https://github.com/vladmandic/automatic">SD.Next</a></summary>

1. SD-WebUI/Comfyサーバーが実行中の場合は閉じます（停止します）
2. （Windowsユーザー向け）：
   - [Visual Studio 2022](https://visualstudio.microsoft.com/downloads/) をインストールします（Communityバージョン - Insightfaceをビルドするためにこの手順が必要です）
   - または [VS C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) のみをインストールし、"Workloads -> Desktop & Mobile" の下の "Desktop Development with C++" を選択します
   - または、VSまたはVS C++ BTをインストールしたくない場合は、[この手順（セクションI）](#insightfacebuild)に従います
3. `extensions\sd-webui-comfyui\ComfyUI\custom_nodes` に移動します
4. コンソールまたはターミナルを開き、`git clone https://github.com/Gourieff/ComfyUI-ReActor` を実行します
5. SD WebUIのルートフォルダに移動し、コンソールまたはターミナルを開き、（Windowsユーザー）`.\venv\Scripts\activate` または（Linux/MacOS）`venv/bin/activate` を実行します
6. `python -m pip install -U pip`
7. `cd extensions\sd-webui-comfyui\ComfyUI\custom_nodes\comfyui-reactor-node`
8. `python install.py`
9.  インストールプロセスが完了するまで待ちます
10. （バージョン0.3.0以降）以下のリンクから追加の顔復元モデルをダウンロードし、`extensions\sd-webui-comfyui\ComfyUI\models\facerestore_models` ディレクトリに保存します：<br>
https://huggingface.co/datasets/Gourieff/ReActor/tree/main/models/facerestore_models
11. SD WebUIを実行し、ReActorノードが実行中であることを示すメッセージがコンソールに表示されるか確認します：
<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/uploads/console_status_running.jpg?raw=true" alt="console_status_running" width="759"/>

12.  ComfyUIタブに移動し、`ReActor` メニュー内または検索でReActorノードを見つけます：
<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/uploads/webui-demo.png?raw=true" alt="webui-demo" width="100%"/>
<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/uploads/search-demo.png?raw=true" alt="webui-demo" width="1043"/>

</details>

<details>
	<summary>スタンドアロン（ポータブル）<a href="https://github.com/comfyanonymous/ComfyUI">ComfyUI</a> for Windows</summary>

1. 次のことを行います：
   - [Visual Studio 2022](https://visualstudio.microsoft.com/downloads/) をインストールします（Communityバージョン - Insightfaceをビルドするためにこの手順が必要です）
   - または [VS C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) のみをインストールし、"Workloads -> Desktop & Mobile" の下の "Desktop Development with C++" を選択します
   - または、VSまたはVS C++ BTをインストールしたくない場合は、[この手順（セクションI）](#insightfacebuild)に従います
2. 2つのオプションから選択します：
   - （ComfyUI Manager）ComfyUI Managerを開き、"Install Custom Nodes" をクリックし、"Search" フィールドに "ReActor" と入力してから "Install" をクリックします。ComfyUIがプロセスを完了したら、サーバーを再起動します。
   - （手動）`ComfyUI\custom_nodes` に移動し、コンソールを開いて `git clone https://github.com/Gourieff/ComfyUI-ReActor` を実行します
3. `ComfyUI\custom_nodes\comfyui-reactor-node` に移動し、`install.bat` を実行します
4. "face_yolov8m.pt" Ultralyticsモデルがない場合は、[Assets](https://huggingface.co/datasets/Gourieff/ReActor/blob/main/models/detection/bbox/face_yolov8m.pt)からダウンロードし、"ComfyUI\models\ultralytics\bbox" ディレクトリに保存してください。
<br>
"Sams" モデルも同様に、[こちら](https://huggingface.co/datasets/Gourieff/ReActor/tree/main/models/sams)からダウンロードし、"ComfyUI\models\sams" ディレクトリに保存してください。
5. ComfyUIを実行し、`ReActor` メニュー内または検索でReActorノードを見つけます

</details>

## 使用方法

ReActorノードは、`ReActor` メニュー内または検索で見つけることができます（検索フィールドに "ReActor" と入力するだけです）

ノードのリスト：
- ••• メインノード •••
   - ReActorFaceSwap（メインノード）
   - ReActorFaceSwapOpt（追加のオプション入力を持つメインノード）
   - ReActorOptions（ReActorFaceSwapOptのオプション）
   - ReActorFaceBoost（フェイスブースターノード）
   - ReActorMaskHelper（マスキングヘルパー）
- ••• 顔モデルの操作 •••
  - ReActorSaveFaceModel（顔モデルの保存）
  - ReActorLoadFaceModel（顔モデルの読み込み）
  - ReActorBuildFaceModel（ブレンドされた顔モデルの作成）
  - ReActorMakeFaceModelBatch（顔モデルバッチの作成）
- ••• 追加のノード •••
  - ReActorRestoreFace（顔の復元）
  - ReActorImageDublicator（1つの画像を画像リストに複製）
  - ImageRGBA2RGB（RGBAをRGBに変換）

すべての必要なスロットを接続し、クエリを実行します。

### メインノードの入力

- `input_image` - 処理する画像（ターゲット画像、SD WebUI拡張機能の "target image" に相当）です。
  - サポートされているノード："Load Image"、"Load Video"、または画像を出力として提供する他のノード。
- `source_image` - `input_image` に交換する顔または顔を持つ画像（ソース画像、SD WebUI拡張機能の "source image" に相当）です。
  - サポートされているノード："Load Image" または画像を出力として提供する他のノード。
- `face_model` - "Load Face Model" ノードまたは他のReActorノードの入力で、以前に "Save Face Model" ノードを介して作成した顔モデルファイル（顔埋め込み）を提供します。
  - サポートされているノード："Load Face Model"、"Build Blended Face Model"。

### メインノードの出力

- `IMAGE` - 結果の画像を持つ出力です。
  - サポートされているノード：画像を入力として持つ任意のノード。
- `FACE_MODEL` - 交換プロセス中に構築されたソース顔のモデルを提供する出力です。
  - サポートされているノード："Save Face Model"、"ReActor"、"Make Face Model Batch"。

### 顔の復元

バージョン0.3.0以降、ReActorノードには組み込みの顔復元機能があります。<br>必要なモデルをダウンロードし（[インストール](#installation)手順を参照）、それらの1つを選択して顔交換中に結果の顔を復元します。これにより、顔の詳細が強化され、結果がより正確になります。

### 顔のインデックス

デフォルトでは、ReActorは画像内の顔を "大きい" から "小さい" 順に検出します。<br>このオプションは、ReActorFaceSwapOptノードとReActorOptionsを追加することで変更できます。

特定の顔を指定する必要がある場合は、ソース画像と入力画像のインデックスを設定できます。

最初に検出された顔のインデックスは0です。

必要な順序でインデックスを設定できます。<br>
例：0,1,2（ソース用）；1,0,2（入力用）。<br>これは、2番目の入力顔（インデックス=1）が最初のソース顔（インデックス=0）によって交換されることを意味します。

### 性別

画像内の検出する性別を指定できます。<br>
ReActorは、指定された条件に一致する場合にのみ顔を交換します。

### 顔モデル

バージョン0.4.0以降、顔モデルを "safetensors" ファイルとして保存し（`ComfyUI\models\reactor\faces` に保存）、ReActorにロードしてさまざまなシナリオを実装し、使用する顔の超軽量な顔モデルを保持できます。

新しいモデルを "Load Face Model" ノードのリストに表示するには、ComfyUI Webアプリケーションのページを更新するだけです。<br>
（ComfyUI Managerを使用することをお勧めします。そうしないと、ページを更新した後にワークフローが失われる可能性があります。更新前に保存していない場合）。

## トラブルシューティング

<a name="insightfacebuild">

### **I. （Windowsユーザー向け）Insightfaceをビルドできない場合や、Visual StudioまたはVS C++ Build Toolsをインストールしたくない場合は、次の手順に従います：**

1. （ComfyUIポータブル）ルートフォルダからPythonのバージョンを確認します：<br>CMDを実行し、`python_embeded\python.exe -V` と入力します
2. 事前にビルドされたInsightfaceパッケージをダウンロードします [Python 3.10用](https://github.com/Gourieff/Assets/raw/main/Insightface/insightface-0.7.3-cp310-cp310-win_amd64.whl) または [Python 3.11用](https://github.com/Gourieff/Assets/raw/main/Insightface/insightface-0.7.3-cp311-cp311-win_amd64.whl)（前の手順で3.11を確認した場合）または [Python 3.12用](https://github.com/Gourieff/Assets/raw/main/Insightface/insightface-0.7.3-cp312-cp312-win_amd64.whl)（前の手順で3.12を確認した場合）をダウンロードし、stable-diffusion-webui（A1111またはSD.Next）のルートフォルダ（"webui-user.bat" ファイルがある場所）またはComfyUIのルートフォルダに保存します
3. ルートフォルダから次のコマンドを実行します：
   - （SD WebUI）CMDを実行し、`.\venv\Scripts\activate`
   - （ComfyUIポータブル）CMDを実行します
4. 次にPIPを更新します：
   - （SD WebUI）`python -m pip install -U pip`
   - （ComfyUIポータブル）`python_embeded\python.exe -m pip install -U pip`
5. 次にInsightfaceをインストールします：
   - （SD WebUI）`pip install insightface-0.7.3-cp310-cp310-win_amd64.whl`（3.10用）または `pip install insightface-0.7.3-cp311-cp311-win_amd64.whl`（3.11用）または `pip install insightface-0.7.3-cp312-cp312-win_amd64.whl`（3.12用）
   - （ComfyUIポータブル）`python_embeded\python.exe -m pip install insightface-0.7.3-cp310-cp310-win_amd64.whl`（3.10用）または `python_embeded\python.exe -m pip install insightface-0.7.3-cp311-cp311-win_amd64.whl`（3.11用）または `python_embeded\python.exe -m pip install insightface-0.7.3-cp312-cp312-win_amd64.whl`（3.12用）
6. 完了！

### **II. "AttributeError: 'NoneType' object has no attribute 'get'"**

このエラーは、モデルファイル `inswapper_128.onnx` に問題がある場合に発生する可能性があります

手動で [こちら](https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx) からダウンロードし、既存のファイルを置き換えて `ComfyUI\models\insightface` に保存します

### **III. "reactor.execute() got an unexpected keyword argument 'reference_image'"**

これは、最新の更新で入力ポイントが変更されたことを意味します<br>
ワークフローから現在のReActorノードを削除し、再度追加します

### **IV. ControlNet Aux Node IMPORT failedエラーがReActorノードと一緒に使用される場合**

1. ComfyUIが実行中の場合は閉じます
2. ComfyUIのルートフォルダに移動し、CMDを開いて次のコマンドを実行します：
   - `python_embeded\python.exe -m pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless`
   - `python_embeded\python.exe -m pip install opencv-python==4.7.0.72`
3. 完了です！

<img src="https://github.com/Gourieff/Assets/blob/main/comfyui-reactor-node/uploads/reactor-w-controlnet.png?raw=true" alt="reactor+controlnet" />

### **V. "ModuleNotFoundError: No module named 'basicsr'" または "subprocess-exited-with-error" がfuture-0.18.3のインストール中に発生する場合**

- ダウンロード https://github.com/Gourieff/Assets/raw/main/comfyui-reactor-node/future-0.18.3-py3-none-any.whl<br>
- ComfyUIのルートに保存し、次のコマンドを実行します：

      python_embeded\python.exe -m pip install future-0.18.3-py3-none-any.whl

- 次に：

      python_embeded\python.exe -m pip install basicsr

### **VI. "fatal: fetch-pack: invalid index-pack output" が `git clone` コマンドを実行しようとしたときに発生する場合"**

`--depth=1`（最後のコミットのみ）を使用してクローンを作成してみてください：

     git clone --depth=1 https://github.com/Gourieff/ComfyUI-ReActor

次に、残りを取得します（必要な場合）：

     git fetch --unshallow

## 更新

この[リポジトリ](https://github.com/Gourieff/sd-webui-extensions-updater)から.batまたは.shスクリプトを `ComfyUI\custom_nodes` ディレクトリに保存し、更新を確認する必要があるときに実行します

### 免責事項

このソフトウェアは、急速に成長しているAI生成メディア業界への生産的な貢献を目的としています。アーティストがカスタムキャラクターのアニメーション化や衣装のモデルとしてキャラクターを使用するなどのタスクを支援します。

このソフトウェアの開発者は、その可能な非倫理的なアプリケーションについて認識しており、それに対する予防措置を講じることを約束します。私たちは、法律と倫理に従いながら、このプロジェクトを前向きな方向に発展させ続けます。

このソフトウェアのユーザーは、地元の法律を遵守しながら、このソフトウェアを責任を持って使用することが期待されています。実在の人物の顔が使用される場合、ユーザーは関係者からの同意を得て、オンラインでコンテンツを投稿する際にそれがディープフェイクであることを明確に示すことをお勧めします。**このソフトウェアの開発者および貢献者は、エンドユーザーの行動に対して責任を負いません。**

この拡張機能を使用することにより、次のようなコンテンツを作成しないことに同意します：
- いかなる法律にも違反するもの；
- 人に害を与えるもの；
- 公共または個人的な情報（画像を含む）を広めるもの；
- 誤情報を広めるもの；
- 脆弱なグループを対象とするもの。

このソフトウェアは、[InsightFace](https://github.com/deepinsight/insightface/) によって提供される事前トレーニング済みモデル `buffalo_l` および `inswapper_128.onnx` を利用しています。これらのモデルは、次の条件の下で提供されます：

[insighfaceライセンスから](https://github.com/deepinsight/insightface/tree/master/python-package)：InsightFaceの事前トレーニング済みモデルは、非商用の研究目的でのみ利用可能です。これには、自動ダウンロードモデルと手動でダウンロードされたモデルの両方が含まれます。

このソフトウェアのユーザーは、これらの使用条件を厳守する必要があります。このソフトウェアの開発者およびメンテナは、InsightFaceの事前トレーニング済みモデルの誤用に対して責任を負いません。

このソフトウェアを商業目的で使用する場合は、独自のモデルをトレーニングするか、商業目的で使用できるモデルを見つける必要があることに注意してください。

### モデルのハッシュサム

#### 安全に使用できるモデルは次のハッシュを持っています：

inswapper_128.onnx
```
MD5:a3a155b90354160350efd66fed6b3d80
SHA256:e4a3f08c753cb72d04e10aa0f7dbe3deebbf39567d4ead6dce08e98aa49e16af
```

1k3d68.onnx

```
MD5:6fb94fcdb0055e3638bf9158e6a108f4
SHA256:df5c06b8a0c12e422b2ed8947b8869faa4105387f199c477af038aa01f9a45cc
```

2d106det.onnx

```
MD5:a3613ef9eb3662b4ef88eb90db1fcf26
SHA256:f001b856447c413801ef5c42091ed0cd516fcd21f2d6b79635b1e733a7109dbf
```

det_10g.onnx

```
MD5:4c10eef5c9e168357a16fdd580fa8371
SHA256:5838f7fe053675b1c7a08b633df49e7af5495cee0493c7dcf6697200b85b5b91
```

genderage.onnx

```
MD5:81c77ba87ab38163b0dec6b26f8e2af2
SHA256:4fde69b1c810857b88c64a335084f1c3fe8f01246c9a191b48c7bb756d6652fb
```

w600k_r50.onnx

```
MD5:80248d427976241cbd1343889ed132b3
SHA256:4c06341c33c2ca1f86781dab0e829f88ad5b64be9fba56e56bc9ebdefc619e43
```

**これらのモデルを未確認のソースからダウンロードする場合は、ハッシュサムを確認してください**

## 感謝とクレジット

<details>
	<summary><a>クリックして展開</a></summary>

<br>

|ファイル|ソース|ライセンス|
|----|------|-------|
|[buffalo_l.zip](https://huggingface.co/datasets/Gourieff/ReActor/blob/main/models/buffalo_l.zip) | [DeepInsight](https://github.com/deepinsight/insightface) | ![license](https://img.shields.io/badge/license-non_commercial-red) |
| [codeformer-v0.1.0.pth](https://huggingface.co/datasets/Gourieff/ReActor/blob/main/models/facerestore_models/codeformer-v0.1.0.pth) | [sczhou](https://github.com/sczhou/CodeFormer) | ![license](https://img.shields.io/badge/license-non_commercial-red) |
| [GFPGANv1.3.pth](https://huggingface.co/datasets/Gourieff/ReActor/blob/main/models/facerestore_models/GFPGANv1.3.pth) | [TencentARC](https://github.com/TencentARC/GFPGAN) | ![license](https://img.shields.io/badge/license-Apache_2.0-green.svg) |
| [GFPGANv1.4.pth](https://huggingface.co/datasets/Gourieff/ReActor/blob/main/models/facerestore_models/GFPGANv1.4.pth) | [TencentARC](https://github.com/TencentARC/GFPGAN) | ![license](https://img.shields.io/badge/license-Apache_2.0-green.svg) |
| [inswapper_128.onnx](https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx) | [DeepInsight](https://github.com/deepinsight/insightface) | ![license](https://img.shields.io
