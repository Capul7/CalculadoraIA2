const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const resultado = document.getElementById("resultado");

navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => { video.srcObject = stream });

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("btnCapturar").addEventListener("click", capturar);
  document.getElementById("btnProcesar").addEventListener("click", procesar);
});

function capturar() {
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  canvas.toBlob(blob => {
    enviarImagen(blob);
  }, "image/jpeg");
}

function procesar() {
  const archivo = document.getElementById("fileInput").files[0];
  if (archivo) {
    enviarImagen(archivo);
  } else {
    resultado.innerText = "⚠️ Sube una imagen o usa la cámara.";
  }
}

function enviarImagen(file) {
  const formData = new FormData();
  formData.append("file", file);

  fetch("/procesar-operacion/", {
    method: "POST",
    body: formData
  })
    .then(resp => resp.json())
    .then(data => {
      if (data.resultado !== undefined) {
        document.getElementById("expresion").innerText = data.expresion;
resultado.innerText = data.resultado;
      } else {
        resultado.innerText = `❌ ${data.error}`;
      }
    })
    .catch(err => {
      resultado.innerText = "❌ Error al procesar la imagen.";
      console.error(err);
    });
}
