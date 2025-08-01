window.addEventListener("DOMContentLoaded", function () {
  // 背景图片列表
  const bgList = window.bgList || [];
  let idx = bgList.indexOf(window.bgImg || "");
  if (idx < 0) idx = 0;
  function setBg(i) {
    if (bgList.length > 0) {
      document.body.style.backgroundImage =
        "url('/resource/" + bgList[i] + "')";
    }
  }
  setBg(idx);
  setInterval(function () {
    idx = (idx + 1) % bgList.length;
    setBg(idx);
  }, 10000);
});

window.addEventListener("DOMContentLoaded", function () {
  const bgList = window.bgList || [];
  let idx = bgList.indexOf(window.bgImg || "");
  if (idx < 0) idx = 0;
  function setBg(i) {
    if (bgList.length > 0) {
      document.body.style.backgroundImage =
        "url('/resource/" + bgList[i] + "')";
    }
  }
  setBg(idx);

  // 自动切换
  setInterval(function () {
    idx = (idx + 1) % bgList.length;
    setBg(idx);
  }, 10000);

  // 点击切换
  document.body.addEventListener("click", function (e) {
    // 避免点击按钮或输入框时切换
    if (
      e.target.tagName === "BUTTON" ||
      e.target.tagName === "A" ||
      e.target.tagName === "INPUT"
    )
      return;
    idx = (idx + 1) % bgList.length;
    setBg(idx);
  });
});
