function textAreaHeightSet(argObj){
 // ==============================================
 //	フォーカス時の背景色リセット
 // ==============================================
  // 一旦テキストエリアを小さくしてスクロールバー（縦の長さを取得）
  argObj.style.height = "10px";
  var wSclollHeight = parseInt(argObj.scrollHeight);
  // 1行の長さを取得する
  var wLineH = parseInt(argObj.style.lineHeight.replace(/px/, ''));
  // 最低2行の表示エリアにする
  if(wSclollHeight < (wLineH * 2)){wSclollHeight=(wLineH * 2);}
  // テキストエリアの高さを設定する
  argObj.style.height = wSclollHeight + "px";
}
