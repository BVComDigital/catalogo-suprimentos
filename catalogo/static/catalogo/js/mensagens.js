document.addEventListener("DOMContentLoaded", function () {
    const mensagens = document.querySelectorAll(".mensagem");

    mensagens.forEach(function (mensagem) {
        setTimeout(function () {
            mensagem.style.opacity = "0";

            setTimeout(function () {
                mensagem.remove();
            }, 500);
        }, 4000);
    });
});