const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const resultado = document.getElementById("resultado");

navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => { video.srcObject = stream })
  .catch(err => {
    console.error("Error al acceder a la cámara:", err);
    resultado.innerText = "⚠️ No se pudo acceder a la cámara.";
  });

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("btnCapturar").addEventListener("click", capturar);
  document.getElementById("btnProcesar").addEventListener("click", procesar);
});

function capturar() {
  try {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(blob => {
      if (blob) {
        enviarImagen(blob);
      } else {
        resultado.innerText = "⚠️ No se pudo capturar la imagen.";
      }
    }, "image/jpeg");
  } catch (error) {
    console.error("Error al capturar:", error);
    resultado.innerText = "❌ Error al capturar la imagen.";
  }
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
    .then(async resp => {
      const contentType = resp.headers.get("content-type");

      if (!contentType || !contentType.includes("application/json")) {
        throw new Error("Respuesta no válida del servidor (no es JSON).");
      }

      const data = await resp.json();

      if (resp.ok) {
        if (data.resultado !== undefined) {
          document.getElementById("expresion").innerText = data.expresion;
          resultado.innerText = data.resultado;
        } else {
          resultado.innerText = `❌ ${data.error}`;
        }
      } else {
        resultado.innerText = `❌ ${data.error || "Error del servidor"}`;
      }
    })
    .catch(err => {
      resultado.innerText = "❌ Error al procesar la imagen.";
      console.error("Error en fetch:", err);
    });
}
