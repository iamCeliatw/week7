document.getElementById("getText").addEventListener("click", getText);
document.getElementById("updateText").addEventListener("click", updateText);
function getText() {
  let input = document.getElementById("userName").value;
  fetch("http://127.0.0.1:3000/api/member?userName=" + input)
    .then((res) => res.json())
    .then((data) => {
      if (data.data === null) {
        document.getElementById("resultText").innerHTML = `查無此帳號`;
      } else {
        document.getElementById(
          "resultText"
        ).innerHTML = `${data.data.name}(${data.data.username})`;
      }
    });
}
function updateText() {
  let updateInput = document.getElementById("updateName").value;
  fetch("http://127.0.0.1:3000/api/member", {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name: updateInput }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        document.getElementById(
          "updatedText"
        ).innerHTML = `更新失敗，請再試一次`;
      } else {
        document.getElementById("updatedText").innerHTML = `更新成功！🎉`;
      }
    });
}
