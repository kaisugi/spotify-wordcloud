# Spotify WordCloud

Spotify WordCloud はあなたのお気に入りのアーティストの名前からワードクラウドを作るアプリです。

AWS: https://spow.tk  
Heroku: https://spotify-wordcloud.herokuapp.com/  
**AWSの方は出費を抑えるためインスタンスを落としていることがあります。**

## URL

| パス   |  メソッド  |  内容  |
|:---|:---|:---|
|  /  |  GET  |  トップ画面の表示  |
|  /login  |  GET  |   Spotify へのログイン |
| /login/spotify/authorized |GET |  Spotify OAuth 認証のコールバック  |    
|  /twitter_auth  |  GET  |  Twitter へのログイン  |    
|  /callback  |  GET  |  Twitter OAuth 認証のコールバック  |    
|  /logout  | GET   |  全てのログアウト（セッションの破棄）  |   
|  /generate  |  GET  |  ワードクラウド画像を作成し, そのバイナリを返す API  |    
|  /regenerate  |  GET  |  ワードクラウド画像を作成し, そのバイナリを返す API （ generate と異なり, キャッシュがあっても強制的に再作成する）  |  
|  /save  |  POST  |  ワードクラウド画像を作成し, 画像を S3 にアップロードした上で, ユーザーID, 作成日時とともに DB に保存する   |    
|  /tweet  |  POST  | ワードクラウド画像を作成し, ツイートする   |    
|  /history  | GET   | 過去に作成した画像一覧の表示  |    
|  /history/:file_hash  |  DELETE  |  指定された画像の削除  |    

**ワードクラウド画像の作成について**

- Spotify の "Get a User's Top Artists" API からトップアーティスト一覧を取得し、1つの文字列として組み合わせてから、それをもとにワードクラウドを作成する。  
組み合わされた文字列はセッションに保持する。また、文字列をハッシュ化したものをファイル名として、作成した画像を `/tmp` フォルダ以下に置く。  
画像作成に関連する URL は常に、まずこれらのキャッシュ情報を最初に参照するように試みる。ただし, /regenerate では `/tmp` フォルダ以下を参照せず, 再び画像を作成する。
