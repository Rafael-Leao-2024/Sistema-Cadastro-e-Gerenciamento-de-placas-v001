
document.addEventListener('DOMContentLoaded', function() {
    const notificacaoBtn = document.getElementById('notificacaoBtn');
    const notificacaoDropdown = document.getElementById('notificacaoDropdown');
    const notificacoesLista = document.getElementById('notificacoesLista');
    const marcarTodasLidas = document.getElementById('marcarTodasLidas');
    const urlMinhasPlacas = document.getElementById('notificacoesLista').dataset.urlMinhasPlacas;


    // Alternar dropdown
    notificacaoBtn.addEventListener('click', function() {
        notificacaoDropdown.classList.toggle('hidden');
        if (!notificacaoDropdown.classList.contains('hidden')) {
            carregarNotificacoes();
        }
    });

    // Fechar dropdown ao clicar fora
    document.addEventListener('click', function(event) {
        if (!notificacaoBtn.contains(event.target) && !notificacaoDropdown.contains(event.target)) {
            notificacaoDropdown.classList.add('hidden');
        }
    });

    // Carregar notificações
    function carregarNotificacoes() {
        fetch('/notificacoes')
            .then(response => response.json())
            .then(notificacoes => {
                if (notificacoes.length === 0) {
                    notificacoesLista.innerHTML = `
                        <div class="p-4 text-center text-gray-500">
                            Nenhuma notificação
                        </div>
                    `;
                    return;
                }

                notificacoesLista.innerHTML = notificacoes.map(notif => `
                    <div class="p-4 border-b ${notif.lida ? 'bg-gray-50' : 'bg-blue-50'}">
                        <div class="flex justify-between items-start">
                            <div class="flex-1">
                                <p class="text-sm ${notif.lida ? 'text-gray-600' : 'text-gray-800 font-medium'}">
                                    <a href="${urlMinhasPlacas.replace('0', notif.id)}">${notif.mensagem}</a>
                                </p>
                                <p class="text-xs text-gray-500 mt-1">${notif.data_criacao}</p>
                            </div>
                            ${!notif.lida ? `
                            <button onclick="marcarComoLida(${notif.id})" 
                                    class="ml-2 p-1 text-blue-600 hover:text-blue-800">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                            d="M5 13l4 4L19 7"></path>
                                </svg>
                            </button>
                            ` : ''}
                        </div>
                    </div>
                `).join('');
            });
    }

    // Marcar notificação como lida
    window.marcarComoLida = function(notificacaoId) {
        fetch(`/marcar-lida/${notificacaoId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                carregarNotificacoes();
                // Recarregar a página para atualizar o contador
                location.reload();
            }
        });
    }

    // Marcar todas como lidas
    marcarTodasLidas.addEventListener('click', function() {
        fetch('/marcar-todas-lidas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                carregarNotificacoes();
                location.reload();
            }
        });
    });
});
