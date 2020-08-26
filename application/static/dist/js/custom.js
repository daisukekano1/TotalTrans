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
function getSelectedText(){
  var text = "";
  var userAgent = window.navigator.userAgent.toLowerCase();
  if(userAgent.indexOf('msie') != -1){
      text = document.selection.createRange().htmlText;
  }else{
      text = window.getSelection().toString();
  }
  return text;
}
function getInputSelection(el) {
    var start = 0, end = 0, normalizedValue, range, textInputRange, len, endRange;
    if (typeof el.selectionStart == "number" && typeof el.selectionEnd == "number") {
        start = el.selectionStart;
        end = el.selectionEnd;
    } else {
        range = document.selection.createRange();

        if (range && range.parentElement() == el) {
            len = el.value.length;
            normalizedValue = el.value.replace(/\r\n/g, "\n");

            // Create a working TextRange that lives only in the input
            textInputRange = el.createTextRange();
            textInputRange.moveToBookmark(range.getBookmark());

            // Check if the start and end of the selection are at the very end
            // of the input, since moveStart/moveEnd doesn't return what we want
            // in those cases
            endRange = el.createTextRange();
            endRange.collapse(false);

            if (textInputRange.compareEndPoints("StartToEnd", endRange) > -1) {
                start = end = len;
            } else {
                start = -textInputRange.moveStart("character", -len);
                start += normalizedValue.slice(0, start).split("\n").length - 1;

                if (textInputRange.compareEndPoints("EndToEnd", endRange) > -1) {
                    end = len;
                } else {
                    end = -textInputRange.moveEnd("character", -len);
                    end += normalizedValue.slice(0, end).split("\n").length - 1;
                }
            }
        }
    }
    return {
        start: start,
        end: end
    };
}
