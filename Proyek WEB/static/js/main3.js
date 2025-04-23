// Ambil elemen input password dan tombol "show"
const passwordInput = document.getElementById("password");
const togglePassword = document.getElementById("toggle-password");

// Saat tombol "show" diklik
togglePassword.addEventListener("click", function () {
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    this.textContent = "Sembunyikan Password";
  } else {
    passwordInput.type = "password";
    this.textContent = "Tunjukkan Password";
  }
});

// Event submit form untuk Sign In
document.getElementById("signin-form").addEventListener("submit", function () {
  
});


