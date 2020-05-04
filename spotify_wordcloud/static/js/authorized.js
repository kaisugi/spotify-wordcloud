var myImage = document.querySelector('.generated');
var result = document.querySelector('.result');
var tweetArea = document.querySelector('.tweet');
var savedArea = document.querySelector('.saved');

function generate() {
  result.innerHTML = "ワードクラウドを作成中...."

  fetch("/generate", {
    cache:"no-cache",
  })
    .then(res => { 
      if (res.status !== 200) {
        throw Error("invalid status");
      }
      return res.blob()
    })
    .then(myBlob => {
      var objectURL = URL.createObjectURL(myBlob);
      myImage.src = objectURL;
      result.innerHTML = "ワードクラウドが作成されました！（直近6ヶ月の記録をもとに作成されています）"
      tweetArea.setAttribute("style", "display: block;")
      savedArea.setAttribute("style", "display: block;")

      var regenerate = document.createElement("a")
      regenerate.setAttribute("onclick", "regenerate()")
      regenerate.setAttribute("style", "color:#000080; cursor:pointer;")
      regenerate.innerHTML = "違うデザインで作り直す"
      result.appendChild(document.createElement("br"))
      result.appendChild(regenerate)
    })
    .catch(e => {
      result.innerHTML = "ワードクラウドの作成に失敗しました。お気に入りのアーティストのデータが不足している可能性があります。"
    })
}

generate();

function regenerate() {
  result.innerHTML = "ワードクラウドを作成中...."

  fetch("/regenerate", {
    cache:"no-cache",
  })
    .then(res => { 
      if (res.status !== 200) {
        throw Error("invalid status");
      }
      return res.blob()
    })
    .then(myBlob => {
      var objectURL = URL.createObjectURL(myBlob);
      myImage.src = objectURL;
      result.innerHTML = "ワードクラウドが作成されました！（直近6ヶ月の記録をもとに作成されています）"
      tweetArea.setAttribute("style", "display: block;")
      savedArea.setAttribute("style", "display: block;")

      var regenerate = document.createElement("a")
      regenerate.setAttribute("onclick", "regenerate()")
      regenerate.setAttribute("style", "color:#000080; cursor:pointer;")
      regenerate.innerHTML = "違うデザインで作り直す"
      result.appendChild(document.createElement("br"))
      result.appendChild(regenerate)
    })
    .catch(e => {
      result.innerHTML = "ワードクラウドの作成に失敗しました。お気に入りのアーティストのデータが不足している可能性があります。"
    })
}

function logout() {
  var url = 'https://accounts.spotify.com/en/logout'                                                                                                                                                                                                                                                                               
  var spotifyLogoutWindow = window.open(url, 'Spotify Logout', 'width=700,height=500,top=40,left=40')                                                                                                
  setTimeout(() => {
    spotifyLogoutWindow.close()
    location.href="/logout"
  }, 1000)
}