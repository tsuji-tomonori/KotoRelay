/* 公開済みDOMだけを検索し、画像dialogの終了時に起点へfocusを戻す。 */
const search = document.querySelector('#search');
search.addEventListener('input', () => {
  const query = search.value.toLocaleLowerCase();
  document.querySelectorAll('article').forEach(article => {
    article.hidden = !article.textContent.toLocaleLowerCase().includes(query);
  });
});
const dialog = document.querySelector('#zoom');
let origin;
document.querySelectorAll('.image').forEach(button => button.addEventListener('click', () => {
  origin = button;
  dialog.querySelector('img').src = button.querySelector('img').src;
  dialog.showModal();
}));
dialog.querySelector('button').addEventListener('click', () => dialog.close());
dialog.addEventListener('close', () => origin?.focus());
