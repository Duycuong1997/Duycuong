// JavaScript = bộ não của trang: phản ứng khi người dùng bấm, gõ...

// 1. "Tìm" các phần tử HTML theo id và cất vào biến
const tenHienThi = document.getElementById("ten-hien-thi");
const oNhap = document.getElementById("o-nhap");
const nutDoiTen = document.getElementById("nut-doi-ten");
const thongBao = document.getElementById("thong-bao");
const dem = document.getElementById("dem");

// 2. Biến đếm (dùng "let" vì giá trị sẽ thay đổi)
let soLanBam = 0;

// 3. Hàm: một đoạn code đặt tên, gọi lại được nhiều lần
function doiTen() {
  soLanBam = soLanBam + 1;
  dem.textContent = soLanBam;

  // .trim() bỏ khoảng trắng thừa ở đầu và cuối
  const tenMoi = oNhap.value.trim();

  if (tenMoi === "") {
    thongBao.textContent = "Bạn chưa nhập tên!";
    return; // dừng hàm tại đây
  }

  tenHienThi.textContent = tenMoi;
  thongBao.textContent = "";
  oNhap.value = "";
}

// 4. Sự kiện: khi bấm nút thì chạy hàm doiTen
nutDoiTen.addEventListener("click", doiTen);

// Bấm phím Enter trong ô nhập cũng đổi tên
oNhap.addEventListener("keydown", function (e) {
  if (e.key === "Enter") {
    doiTen();
  }
});
