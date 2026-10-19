import streamlit as st

# 1 - Configuração da página (título e ícone da aba)
st.set_page_config(page_title="Calculadora do Mercado", page_icon="🛒", layout="centered")

st.title("🛒 Calculadora do Supermercado")
st.caption("Selecione os produtos, veja o total e calcule o troco.")

# 2 - Dicionário com os itens e seus preços
precos_itens = {
    "Arroz (5kg)": 25.90,
    "Feijão (1kg)": 8.50,
    "Açúcar (1kg)": 4.99,
    "Café (500g)": 18.90,
    "Óleo de soja (900ml)": 7.49,
    "Macarrão (500g)": 4.29,
    "Leite integral (1L)": 5.39,
    "Pão de forma": 8.99,
    "Manteiga (200g)": 11.90,
    "Ovos (dúzia)": 12.50,
    "Queijo muçarela (kg)": 42.90,
    "Presunto (kg)": 32.90,
    "Frango (kg)": 14.90,
    "Carne moída (kg)": 36.90,
    "Banana (kg)": 5.99,
    "Tomate (kg)": 7.90,
    "Batata (kg)": 6.49,
    "Cebola (kg)": 5.49,
    "Sabão em pó (1kg)": 15.90,
    "Papel higiênico (12 rolos)": 21.90,
    "Detergente (500ml)": 2.79,
    "Refrigerante (2L)": 9.99,
}

# Cédulas e moedas do Real (em centavos, para evitar erro de arredondamento)
CEDULAS_MOEDAS = [
    (20000, "Cédula de R$ 200"),
    (10000, "Cédula de R$ 100"),
    (5000, "Cédula de R$ 50"),
    (2000, "Cédula de R$ 20"),
    (1000, "Cédula de R$ 10"),
    (500, "Cédula de R$ 5"),
    (200, "Cédula de R$ 2"),
    (100, "Moeda de R$ 1"),
    (50, "Moeda de R$ 0,50"),
    (25, "Moeda de R$ 0,25"),
    (10, "Moeda de R$ 0,10"),
    (5, "Moeda de R$ 0,05"),
    (1, "Moeda de R$ 0,01"),
]


def formatar_real(valor):
    """Formata um número no padrão brasileiro: R$ 1.234,56"""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


# 3 - Função para calcular o preço total da compra
def calcular_preco_total(itens_selecionados):
    total = sum(precos_itens[item] for item in itens_selecionados)
    return total


# 4 - Função para calcular o troco
def calcular_troco(valor_pago, total):
    return valor_pago - total


# 5 - Função que separa o troco em cédulas e moedas
def separar_troco(troco):
    restante = round(troco * 100)  # trabalha em centavos
    resultado = []
    for valor, nome in CEDULAS_MOEDAS:
        quantidade = restante // valor
        if quantidade > 0:
            resultado.append((nome, quantidade))
            restante -= quantidade * valor
    return resultado


# 6 - Multiselect para escolher vários itens
itens_selecionados = st.multiselect(
    label="Selecione os itens do supermercado:",
    options=list(precos_itens.keys()),
    placeholder="Escolha os produtos...",
)

# 7 - Exibição dos detalhes e cálculo
if itens_selecionados:
    st.subheader("Itens Selecionados:")
    for item in itens_selecionados:
        st.write(f"- {item}: {formatar_real(precos_itens[item])}")

    # Chamada da função para calcular o preço total
    total_compra = calcular_preco_total(itens_selecionados)

    st.divider()
    col1, col2 = st.columns(2)
    col1.metric(label="Total da Compra", value=formatar_real(total_compra))
    col2.metric(label="Quantidade de itens", value=len(itens_selecionados))

    # 8 - Calculadora de troco
    st.divider()
    st.subheader("💵 Pagamento e Troco")

    forma_pagamento = st.radio(
        "Forma de pagamento:",
        ["Dinheiro", "PIX", "Cartão"],
        horizontal=True,
    )

    if forma_pagamento == "Dinheiro":
        valor_pago = st.number_input(
            "Valor entregue pelo cliente (R$):",
            min_value=0.0,
            value=0.0,
            step=5.0,
            format="%.2f",
        )

        if valor_pago == 0:
            st.info("Digite o valor recebido para calcular o troco.")
        else:
            troco = calcular_troco(valor_pago, total_compra)

            if troco < -0.004:
                st.error(f"Valor insuficiente! Faltam {formatar_real(-troco)}.")
            elif troco < 0.005:
                st.success("Valor exato! Não há troco. ✅")
                st.balloons()
            else:
                st.metric(label="Troco", value=formatar_real(troco))

                with st.expander("Como entregar o troco (cédulas e moedas)", expanded=True):
                    for nome, quantidade in separar_troco(troco):
                        st.write(f"- {quantidade}x {nome}")
    else:
        st.success(
            f"Pagamento via {forma_pagamento}: cobrar exatamente "
            f"{formatar_real(total_compra)}. Não há troco."
        )
else:
    st.info("Nenhum item selecionado. Marque os produtos acima para ver o valor total.")
