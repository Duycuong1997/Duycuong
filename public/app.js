// Hiện / ẩn mật khẩu
document.querySelectorAll('.toggle-password').forEach((btn) => {
  btn.addEventListener('click', () => {
    const input = document.getElementById(btn.dataset.target);
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    btn.textContent = show ? 'Ẩn' : 'Hiện';
  });
});

function showMessage(text, type) {
  const box = document.getElementById('message');
  box.textContent = text;
  box.className = `message ${type}`;
}

// Gửi form bằng fetch và hiển thị kết quả
function handleForm(formId, url, onSuccess) {
  const form = document.getElementById(formId);
  const submitBtn = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    submitBtn.disabled = true;

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(Object.fromEntries(new FormData(form))),
      });
      const data = await res.json();

      if (!res.ok) {
        showMessage(data.error || 'Đã có lỗi xảy ra.', 'error');
        return;
      }

      showMessage(data.message, 'success');
      if (onSuccess) onSuccess(data);
      else if (data.redirect) window.location.href = data.redirect;
    } catch {
      showMessage('Không thể kết nối tới máy chủ.', 'error');
    } finally {
      submitBtn.disabled = false;
    }
  });
}
