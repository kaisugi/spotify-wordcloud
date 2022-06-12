var myImage = document.querySelector(".generated");
var result = document.querySelector(".result");
var hideFirstAreas = document.querySelectorAll(".hide-first");
var saveImageText = document.querySelector(".saveimagetext");

var generatingMessage =
  '<div class="loading"></div> <span>ワードクラウドを作成中....</span><span>（最大10秒程度かかります）</span>';
var successMessage =
  "ワードクラウドが作成されました！（直近6ヶ月の記録をもとに作成されています）";
var failureMessage =
  "ワードクラウドの作成に失敗しました。お気に入りのアーティストのデータが不足している可能性があります。";
var retryMessage = "違うデザインで作り直す";

function generate() {
  result.innerHTML = generatingMessage;

  fetch("/generate", {
    cache: "no-cache",
  })
    .then((res) => {
      if (res.status !== 200) {
        throw Error("invalid status");
      }
      return res.blob();
    })
    .then((myBlob) => {
      var objectURL = URL.createObjectURL(myBlob);
      myImage.src = objectURL;
      result.innerHTML = successMessage;
      for (const area of hideFirstAreas) {
        area.setAttribute("style", "display: block;");
      }

      var regenerate = document.createElement("a");
      regenerate.setAttribute("onclick", "regenerate()");
      regenerate.setAttribute("style", "color:#212eaa; cursor:pointer;");
      regenerate.innerHTML = retryMessage;
      result.appendChild(document.createElement("br"));
      result.appendChild(regenerate);
    })
    .catch((e) => {
      result.innerHTML = failureMessage;
    });
}

generate();

function regenerate() {
  result.innerHTML = generatingMessage;

  fetch("/regenerate", {
    cache: "no-cache",
  })
    .then((res) => {
      if (res.status !== 200) {
        throw Error("invalid status");
      }
      return res.blob();
    })
    .then((myBlob) => {
      var objectURL = URL.createObjectURL(myBlob);
      myImage.src = objectURL;
      result.innerHTML = successMessage;
      for (const area of hideFirstAreas) {
        area.setAttribute("style", "display: block;");
      }

      var regenerate = document.createElement("a");
      regenerate.setAttribute("onclick", "regenerate()");
      regenerate.setAttribute("style", "color:#212eaa; cursor:pointer;");
      regenerate.innerHTML = retryMessage;
      result.appendChild(document.createElement("br"));
      result.appendChild(regenerate);
    })
    .catch((e) => {
      result.innerHTML = failureMessage;
    });
}

function afterSubmission() {
  saveImageText.innerHTML = '<h3 style="color: black;">保存中...</h3>';
}

function imageLinkCopy() {
  fetch("/shareLink", {
    cache: "no-cache",
  })
    .then((res) => {
      if (res.status !== 200) {
        throw Error("invalid status");
      }
      return res.json();
    })
    .then((data) => {
      window.prompt("画像付きリンクを作成しました！\nこのリンクを LINE や Slack、Discord などに貼り付けるとワードクラウドも表示されます。", data["link"]);
    })
    .catch((e) => {
      alert("エラーが発生しました。");
    });
}

function logout() {
  var url = "https://accounts.spotify.com/en/logout";
  var spotifyLogoutWindow = window.open(
    url,
    "Spotify Logout",
    "width=700,height=500,top=40,left=40"
  );
  setTimeout(() => {
    spotifyLogoutWindow.close();
    location.href = "/logout";
  }, 1000);
}
