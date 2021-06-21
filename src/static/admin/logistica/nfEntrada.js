document.addEventListener('DOMContentLoaded', nfEntradaReady, false);

async function get_data(cadastro) {
    let url = '/logistica/ajax/entr_nf_cadastro/'+cadastro;
    let nfEntrada_obj = null;

    
    try {
        nfEntrada_obj = await (await fetch(url)).json();
    } catch(e) {
        console.log('erro buscando cadastro', cadastro);
    }
    
    document.getElementById('id_emissor').value = nfEntrada_obj.emissor;
    document.getElementById('id_descricao').value = nfEntrada_obj.descricao;
    document.getElementById('id_transportadora').value = nfEntrada_obj.transportadora;

}

function nfEntradaReady () {

    const i_cadastro = document.getElementById('id_cadastro');
    
    if (i_cadastro) {
        i_cadastro.addEventListener('focusout', (event) => {
            get_data(i_cadastro.value);
        });
    }
}
  
