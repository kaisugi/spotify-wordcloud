var myImage = document.querySelector('.generated');
var result = document.querySelector('.result');
var tweetArea = document.querySelector('.tweet');
var savedArea = document.querySelector('.saved');

var successMessage = "ワードクラウドが作成されました！（直近6ヶ月の記録をもとに作成されています）";
var failureMessage = "ワードクラウドの作成に失敗しました。お気に入りのアーティストのデータが不足している可能性があります。";
var retryMessage = "違うデザインで作り直す";

function generate() {
  result.innerHTML = '<img src="https://res.cloudinary.com/hellorusk/image/upload/v1611155857/loading.svg?' + (new Date).getTime() + '"> ワードクラウドを作成中....';

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
      result.innerHTML = successMessage;
      tweetArea.setAttribute("style", "display: block;")
      savedArea.setAttribute("style", "display: block;")

      var regenerate = document.createElement("a")
      regenerate.setAttribute("onclick", "regenerate()")
      regenerate.setAttribute("style", "color:#212eaa; cursor:pointer;")
      regenerate.innerHTML = retryMessage;
      result.appendChild(document.createElement("br"))
      result.appendChild(regenerate)
    })
    .catch(e => {
      result.innerHTML = failureMessage;
    })
}

generate();

function regenerate() {
  result.innerHTML = '<img src="https://res.cloudinary.com/hellorusk/image/upload/v1611155857/loading.svg?' + (new Date).getTime() + '"> ワードクラウドを作成中....';

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
      result.innerHTML = successMessage;
      tweetArea.setAttribute("style", "display: block;")
      savedArea.setAttribute("style", "display: block;")

      var regenerate = document.createElement("a")
      regenerate.setAttribute("onclick", "regenerate()")
      regenerate.setAttribute("style", "color:#212eaa; cursor:pointer;")
      regenerate.innerHTML = retryMessage;
      result.appendChild(document.createElement("br"))
      result.appendChild(regenerate)
    })
    .catch(e => {
      result.innerHTML = failureMessage;
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