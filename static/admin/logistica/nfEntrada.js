document.addEventListener('DOMContentLoaded', nfEntradaReady, false);

async function get_data(cadastro) {
    let url = '/logistica/ajax/entr_nf_cadastro/'+cadastro;
    let nfEntrada_obj = null;

    
    try {
        nfEntrada_obj = await (await fetch(url)).json();
        document.getElementById('id_cadastro').value = nfEntrada_obj.cadastro;
        document.getElementById('id_emissor').value = nfEntrada_obj.emissor;
        document.getElementById('id_descricao').value = nfEntrada_obj.descricao;
        document.getElementById('id_transportadora').value = nfEntrada_obj.transportadora;
        if ('motorista' in nfEntrada_obj) {
            document.getElementById('id_motorista').value = nfEntrada_obj.motorista;
        }
        if ('placa' in nfEntrada_obj) {
            document.getElementById('id_placa').value = nfEntrada_obj.placa;
        }
    } catch(e) {
        console.log('erro buscando cadastro', cadastro);
    }
    
}

function nfEntradaReady () {

    const i_cadastro = document.getElementById('id_cadastro');
    
    if (i_cadastro) {
        i_cadastro.addEventListener('focusout', (event) => {
            let cadastro = i_cadastro.value.replace(/[^\d]/g, '');
            get_data(cadastro);
        });
    }
}
  
