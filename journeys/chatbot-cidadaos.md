<!-- { section: "39d5618f-837b-44a0-952d-2dde9274012d", x: 0, y: 0} -->

```stack
trigger(on: "CATCH ALL")

```

<!-- { section: "89ad4645-427f-4e61-a7f0-0751188924ca", x: 504, y: 0} -->

```stack
card Branch_d980e1, "Branch_d980e1", code_generator: "CONDITIONALS" do
  then(Branch_ec97eb when event.message.button.text == "QUERO BUSCAR ATENDIMENTO")
  then(Text_9b406e when event.message.button.text == "JÁ FIZ O EXAME")
  then(Text_9b406e when event.message.button.text == "NÃO SOU EU")
  then(Text_9b406e when event.message.button.text == "JÁ FUI ATENDIDO(A)")
  then(Text_058211)
end

```

<!-- { section: "dc8b6e97-be0e-4e48-acd6-e46400ba4819", x: 1032, y: 408} -->

```stack
card Text_058211, "Text_058211", code_generator: "TEXT_MESSAGE" do
  text(
    "Esse número pertence a @number.display_name. Neste momento estamos utilizando ele apenas para campanhas de saúde, não conseguimos responder individualmente. Procure sua unidade de referência para dúvidas."
  )
end

```

<!-- { section: "97a495df-2598-4325-81e7-d19cd6dd520b", x: 1032, y: 120} -->

```stack
card Text_9b406e, "Text_9b406e", code_generator: "TEXT_MESSAGE" do
  text("Obrigada pelo seu retorno.

Desculpe a inconveniência, estamos trabalhando para melhorar nossos serviços.")
end

```

<!-- { section: "43816ed0-4225-46b9-a99b-aa2e27656c44", x: 1680, y: -1152} -->

```stack
card Text_635538, "Text_635538", code_generator: "TEXT_MESSAGE" do
  text("*@contact.estabelecimento_nome* 
@contact.estabelecimento_telefone
@contact.estabelecimento_horario
---
🏡 *Endereço*: @contact.estabelecimento_endereco.
---
📍 É necessário comparecer 
à unidade de saúde portando: *@contact.estabelecimento_documentos .* Caso não tenha o(s) documento(s) procure a unidade para mais informações.

➡️ É realizado a coleta do citopatológico: @contact.horarios_cito .

😀 Aguardamos por você!")
end

```

<!-- { section: "47c32f31-7cd8-479b-bb60-37510f60629d", x: 1032, y: -528} -->

```stack
card Branch_ec97eb, "Branch_ec97eb", code_generator: "CONDITIONALS" do
  then(Text_635538 when has_phrase(contact.linha_de_cuidado, "cito"))
  then(Text_635538_060e7c)
end

```

<!-- { section: "f5a00bb2-4bf8-47b0-8139-4b97bf86c217", x: 1656, y: 144} -->

```stack
card Text_635538_060e7c, "Text_635538_060e7c", code_generator: "TEXT_MESSAGE" do
  text("*@contact.estabelecimento_nome* 
@contact.estabelecimento_telefone
@contact.estabelecimento_horario
---
🏡 *Endereço*: @contact.estabelecimento_endereco.
---
📍 É necessário comparecer 
à unidade de saúde portando: *@contact.estabelecimento_documentos .* Caso não tenha o(s) documento(s) procure a unidade para mais informações.

➡️ Este atendimento é realizado: @contact.horarios_cronicos .

😀 Aguardamos por você!")
end

```

<!-- { section: "0f1c5f77-6cb8-4424-a41b-52a2ced3abb2", x: -1000, y: 0} -->

```stack
card RESERVED_DEFAULT_CARD, "RESERVED_DEFAULT_CARD", code_generator: "RESERVED_DEFAULT_CARD" do
  # RESERVED_DEFAULT_CARD
end

```

<!-- { section: "INTERACTION_TIMEOUT_CELL", x: 0, y: 0} -->

```stack
interaction_timeout(120)

```