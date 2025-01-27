<!-- { section: "8c0ece70-4c75-49c8-a967-d7e33e1cc2bb", x: -264, y: 0} -->

```stack
trigger(on: "CATCH ALL")

```

<!-- { section: "d3f87bd7-c022-41b0-bc5b-c7a05d9e2549", x: 120, y: 0} -->

```stack
card Branch_d980e1, "Branch_d980e1", code_generator: "CONDITIONALS" do
  then(Branch_ec97eb when event.message.button.text == "QUERO BUSCAR ATENDIMENTO")
  then(Text_9b406e when event.message.button.text == "JÁ FIZ O EXAME")
  then(Text_9b406e when event.message.button.text == "NÃO SOU EU")
  then(Text_9b406e when event.message.button.text == "JÁ FUI ATENDIDO(A)")
  then(Text_058211)
end

```

<!-- { section: "879ba17f-7172-4805-aa7b-182481ac7f6b", x: 1008, y: 600} -->

```stack
card Text_058211, "Text_058211", code_generator: "TEXT_MESSAGE" do
  text(
    "Esse número pertence a @number.display_name. Neste momento estamos utilizando ele apenas para campanhas de saúde, não conseguimos responder individualmente. Procure sua unidade de referência para dúvidas."
  )
end

```

<!-- { section: "abfadf53-dc78-4412-a61c-129a1c726e24", x: 744, y: 192} -->

```stack
card Text_9b406e, "Text_9b406e", code_generator: "TEXT_MESSAGE" do
  text("Obrigada pelo seu retorno.

Desculpe a inconveniência, estamos trabalhando para melhorar nossos serviços.")
end

```

<!-- { section: "36aaf17c-e9be-4fd6-9c71-ae25a9a8793d", x: 1776, y: -1176} -->

```stack
card Text_635538, "Text_635538", code_generator: "TEXT_MESSAGE" do
  text("*@contact.estabelecimento_nome* 
@contact.estabelecimento_telefone
@contact.estabelecimento_horario
---
🏡 *Endereço*: @contact.estabelecimento_endereco.
---

➡️ É realizado a coleta do citopatológico: @contact.horarios_cito .

_Vale lembrar: o exame não pode ser realizado em caso de menstruação ou relação sexual dois dias antes. 😉_

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

<!-- { section: "1ec545ea-52fb-4f23-ae6c-cac28a534e15", x: 1776, y: -384} -->

```stack
card Text_635538_060e7c, "Text_635538_060e7c", code_generator: "TEXT_MESSAGE" do
  text("*@contact.estabelecimento_nome* 
@contact.estabelecimento_telefone
@contact.estabelecimento_horario
---
🏡 *Endereço*: @contact.estabelecimento_endereco.
---

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
interaction_timeout(86400)

```