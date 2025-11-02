function calcularLucro() {
    // 1. Coletar os valores dos inputs (sempre em R$)
    const precoVenda = parseFloat(document.getElementById('precoVenda').value) || 0;
    const custoMaterial = parseFloat(document.getElementById('custoMaterial').value) || 0;
    const taxaMarketplacePct = parseFloat(document.getElementById('taxaMarketplace').value) || 0;
    const custosVariaveisPct = parseFloat(document.getElementById('custosVariaveis').value) || 0; // Usando como percentual por agora

    // 2. Calcular o valor das taxas (em R$)
    const taxaMarketplaceValor = precoVenda * (taxaMarketplacePct / 100);
    const custosVariaveisValor = precoVenda * (custosVariaveisPct / 100);

    // 3. Calcular os custos totais
    const custosTotais = custoMaterial + taxaMarketplaceValor + custosVariaveisValor;

    // 4. Calcular o lucro
    const lucroBruto = precoVenda - custoMaterial;
    const lucroReal = precoVenda - custosTotais;

    // 5. Exibir os resultados na página
    document.getElementById('lucroBruto').textContent = `R$ ${lucroBruto.toFixed(2)}`;
    document.getElementById('taxasTotais').textContent = `R$ ${(custosTotais - custoMaterial).toFixed(2)}`;
    document.getElementById('lucroReal').textContent = `R$ ${lucroReal.toFixed(2)}`;
    
    // Opcional: Feedback visual
    if (lucroReal > 0) {
        document.getElementById('lucroReal').style.color = 'green';
    } else {
        document.getElementById('lucroReal').style.color = 'red';
    }
}
