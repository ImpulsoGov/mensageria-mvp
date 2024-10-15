<!-- { section: "789bee2e-e9aa-4a98-8794-fdd932bb62a4", x: -1584, y: 0} -->

```stack
trigger(on: "MESSAGE RECEIVED") when event.message.button.text == "AJUSTAR INFORMAÇÕES"

trigger(on: "MESSAGE RECEIVED") when event.message.button.text == "CONFIRMO!"

trigger(on: "MESSAGE RECEIVED") when event.message.button.text == "OUTROS"

```

<!-- { section: "691cfd61-7f0e-464b-bb1b-6ea71b1d57d1", x: -1056, y: 0} -->

```stack
card Insight_059375, "Insight_059375", code_generator: "WRITE_RESULTS" do
  write_result("telefone", "@Contact.telefone")
  then(Insight_1dde8f)
end

```

<!-- { section: "8a884a1d-b55b-4a0d-8c9c-fdaba8d36122", x: -72, y: 0} -->

```stack
card Branch_8121a5, "Branch_8121a5", code_generator: "CONDITIONALS" do
  then(Buttons_9f109d when event.message.button.text == "OUTROS")
  then(Ajustar_info_inicio when event.message.button.text == "AJUSTAR INFORMAÇÕES")
  then(Informacoes_inicio_confirmadas when event.message.button.text == "CONFIRMO!")
  then(RESERVED_DEFAULT_CARD)
end

```

<!-- { section: "fb27fc11-6cdc-4e59-9381-545d766ebb10", x: 1464, y: 48} -->

```stack
card Informacoes_inicio_confirmadas, "Informacoes_inicio_confirmadas",
  code_generator: "TEXT_MESSAGE" do
  text("Obrigada pelo seu retorno.

Informações confirmadas!")
  then(Botao_confirmacao_disp_cito)
end

```

<!-- { section: "f2ea4379-0585-4329-a202-5b830dece423", x: 2208, y: 1104} -->

```stack
card Font_styleverticalalign_inheritfont_styleverticalalign_inheritNao_sou_desta_unidadefontfont,
     "Font_styleverticalalign_inheritfont_styleverticalalign_inheritNao_sou_desta_unidadefontfont",
     code_generator: "TEXT_MESSAGE" do
  text("Obrigada pelo seu retorno.

Desculpe a inconveniência, estamos trabalhando para melhorar nossos serviços.")
end

```

<!-- { section: "aa054027-ac81-43b8-a0b7-9ea3c8952496", x: 1632, y: 264} -->

```stack
card Ajustar_info_inicio, "Ajustar_info_inicio", code_generator: "QUESTION" do
  ref_Ajustar_info_inicio = ask("Certo, vamos ajustar!

Por favor, envie as informações corretas de funcionamento e contato da sua Unidade de Saúde.")
  write_result("funcionamento_unidade", ref_Ajustar_info_inicio)
  then(Botao_confirmacao_func_unidade)
end

```

<!-- { section: "9898198d-8460-448d-9993-2de6b032aafa", x: 2856, y: 480} -->

```stack
card Botao_confirmacao_disp_cito, "Botao_confirmacao_disp_cito",
  code_generator: "REPLY_BUTTON_TEXT" do
  ref_Botao_confirmacao_disp_cito =
    buttons(["CONFIRMO! ✅", "AJUSTAR INFORMAÇÃO", "VOLTAR AO INÍCIO "]) do
      text(
        "Em relação à oferta de atendimento para *coleta de citopatológico/preventivo* na sua unidade, a disponibilidade abaixo esta correta?

_\"Realizamos a coleta do citopatológico @contact.horarios_cito .\"_"
      )
    end

  then(Obrigado_pelas_info_ee6f35 when ref_Botao_confirmacao_disp_cito == "CONFIRMO! ✅")
  then(Ajusta_disp_cito when ref_Botao_confirmacao_disp_cito == "AJUSTAR INFORMAÇÃO")
  then(Template_ff3800 when ref_Botao_confirmacao_disp_cito == "VOLTAR AO INÍCIO ")
end

```

<!-- { section: "8b0285e2-e73a-4f4a-a6f5-6a6c769cdcee", x: 3288, y: 1320} -->

```stack
card Ajusta_disp_cito, "Ajusta_disp_cito", code_generator: "QUESTION" do
  ref_Ajusta_disp_cito =
    ask("Certo, vamos ajustar!

Por favor envie as informações corretas de oferta de atendimento para coleta de citopatológico.")

  write_result("oferta_cito", ref_Ajusta_disp_cito)
  then(Botao_confirma_ajuste_disp_cito)
end

```

<!-- { section: "80ec4ee3-a3e1-4017-aa01-50786003f8f8", x: 3552, y: 840} -->

```stack
card Obrigado_pelas_info_ee6f35, "Obrigado_pelas_info_ee6f35", code_generator: "TEXT_MESSAGE" do
  text("Obrigado pelas informações! ")
  then(Botao_confirmacao_disp_cronicos)
end

```

<!-- { section: "47004f68-17aa-4149-a2cc-bf408cc8bea9", x: 2208, y: 624} -->

```stack
card Botao_confirmacao_func_unidade, "Botao_confirmacao_func_unidade",
  code_generator: "REPLY_BUTTON_TEXT" do
  ref_Botao_confirmacao_func_unidade =
    buttons(["CONFIRMO!  ✅", "AJUSTAR INFORMAÇÕES"]) do
      text(
        "Você confirma as informações abaixo de funcionamento e contato da sua Unidade de Saúde?

@event.message.text.body "
      )
    end

  then(Botao_confirmacao_disp_cito when ref_Botao_confirmacao_func_unidade == "CONFIRMO!  ✅")
  then(Ajustar_info_inicio when ref_Botao_confirmacao_func_unidade == "AJUSTAR INFORMAÇÕES")
end

```

<!-- { section: "7894214c-8ca0-4627-9d67-89b0b9bfb347", x: 3768, y: 1320} -->

```stack
card Botao_confirma_ajuste_disp_cito, "Botao_confirma_ajuste_disp_cito",
  code_generator: "REPLY_BUTTON_TEXT" do
  ref_Botao_confirma_ajuste_disp_cito =
    buttons(["CONFIRMO! ✅", "AJUSTAR INFORMAÇÃO"]) do
      text(
        "Em relação à oferta de atendimento para *coleta de citopatológico/preventivo* na sua unidade, as disponibilidades abaixo estão corretas?
  
_\"Realizamos a coleta do citopatológico_ 
_@event.message.text.body \"_"
      )
    end

  then(
    Obrigado_pelas_info_ee6f35_36fbfd
    when ref_Botao_confirma_ajuste_disp_cito == "CONFIRMO! ✅"
  )

  then(Ajusta_disp_cito when ref_Botao_confirma_ajuste_disp_cito == "AJUSTAR INFORMAÇÃO")
end

```

<!-- { section: "28611b37-f010-449e-a105-d372a721cf18", x: 4264, y: 1320} -->

```stack
card Obrigado_pelas_info_ee6f35_36fbfd, "Obrigado_pelas_info_ee6f35_36fbfd",
  code_generator: "TEXT_MESSAGE" do
  text("Obrigado pelas informações! ")
  then(Botao_confirmacao_disp_cronicos)
end

```

<!-- { section: "08116de5-0599-4bfa-8b2d-3bb73299a066", x: 4728, y: 1152} -->

```stack
card Botao_confirmacao_disp_cronicos, "Botao_confirmacao_disp_cronicos",
  code_generator: "REPLY_BUTTON_TEXT" do
  ref_Botao_confirmacao_disp_cronicos =
    buttons(["CONFIRMO! ✅", "AJUSTAR INFORMAÇÃO", "VOLTAR "]) do
      text(
        "Em relação à oferta de atendimento para *pessoas com condições crônicas (hipertensão e/ou diabetes)* na sua unidade, as disponibilidades abaixo estão corretas?

_\"Realizamos atendimento para pessoas com doenças crônicas  @contact.horarios_cronicos.\"_"
      )
    end

  then(Insight_9e6067 when ref_Botao_confirmacao_disp_cronicos == "CONFIRMO! ✅")
  then(Ajusta_disp_cronicos when ref_Botao_confirmacao_disp_cronicos == "AJUSTAR INFORMAÇÃO")
  then(Botao_confirmacao_disp_cito when ref_Botao_confirmacao_disp_cronicos == "VOLTAR ")
end

```

<!-- { section: "06966b04-a508-4e16-8b63-307715fbf66d", x: 5184, y: 2184} -->

```stack
card Ajusta_disp_cronicos, "Ajusta_disp_cronicos", code_generator: "QUESTION" do
  ref_Ajusta_disp_cronicos =
    ask(
      "Certo, vamos ajustar!

Por favor envie as informações corretas de oferta de atendimento para pessoas com condições crônicas."
    )

  write_result("oferta_cronicos", ref_Ajusta_disp_cronicos)
  then(Botao_confirma_ajuste_disp_cronicos)
end

```

<!-- { section: "0532d216-2c66-4092-ab14-5d0f9d353ac4", x: 5784, y: 2328} -->

```stack
card Botao_confirma_ajuste_disp_cronicos, "Botao_confirma_ajuste_disp_cronicos",
  code_generator: "REPLY_BUTTON_TEXT" do
  ref_Botao_confirma_ajuste_disp_cronicos =
    buttons(["CONFIRMO! ✅", "AJUSTAR INFORMAÇÃO"]) do
      text(
        "Em relação à oferta de atendimento para *pessoas com condições crônicas(hipertensão ou diabetes)* na sua unidade, as disponibilidades abaixo estão corretas?
  
_\"Realizamos atendimento para pessoas com doenças crônicas @event.message.text.body \"_"
      )
    end

  then(Insight_9e6067 when ref_Botao_confirma_ajuste_disp_cronicos == "CONFIRMO! ✅")

  then(
    Ajusta_disp_cronicos
    when ref_Botao_confirma_ajuste_disp_cronicos == "AJUSTAR INFORMAÇÃO"
  )
end

```

<!-- { section: "60ae44d3-bc1e-4fdd-9718-ab51e753bf17", x: 7320, y: 2112} -->

```stack
card Obrigado_pelas_info_ee6f35_3765f0_ace2e4, "Obrigado_pelas_info_ee6f35_3765f0_ace2e4",
  code_generator: "TEXT_MESSAGE" do
  text("Obrigado pelas informações! ")
end

```

<!-- { section: "8d9ae6c1-cb77-4994-87ba-1e11e792f181", x: 1296, y: 960} -->

```stack
card Buttons_9f109d, "Buttons_9f109d", code_generator: "REPLY_BUTTON_TEXT" do
  ref_Buttons_9f109d =
    buttons(["NÃO SOU DESTA EQUIPE", "NÃO SOU EU", "SABER MAIS"]) do
      text("Selecione a opção que melhor descreve a sua situação:")
    end

  then(Inicia_situacao_outros when ref_Buttons_9f109d == "NÃO SOU DESTA EQUIPE")
  then(Inicia_situacao_outros when ref_Buttons_9f109d == "NÃO SOU EU")
  then(Buttons_6bbbd2 when ref_Buttons_9f109d == "SABER MAIS")
end

```

<!-- { section: "49892d13-2880-4f45-be33-c7b79dfd078d", x: 1776, y: 1416} -->

```stack
card Buttons_6bbbd2, "Buttons_6bbbd2", code_generator: "REPLY_BUTTON_TEXT" do
  ref_Buttons_6bbbd2 =
    buttons(["IR CONFIRMAR! ✅", "FALAR COM ATENDENTE", "VER MENSAGEM"]) do
      text(
        "Essa é uma iniciativa da Impulso Gov, parte do projeto Impulso Previne que dispara mensagem para o publico da sua equipe incentivando-o a ir a unidade de referência.

Se desejar mais informações ou não quiser participar da iniciativa clique para falar com um(a) de nossos(a) atendentes.
"
      )
    end

  then(Template_ff3800 when ref_Buttons_6bbbd2 == "IR CONFIRMAR! ✅")
  then(HANDOVER_STARTS_a48888 when ref_Buttons_6bbbd2 == "FALAR COM ATENDENTE")
  then(Buttons_1f4682 when ref_Buttons_6bbbd2 == "VER MENSAGEM")
end

```

<!-- { section: "804de377-51c8-4d0f-9f64-670a1538c6df", x: 480, y: -1104} -->

```stack
card Template_ff3800, "Template_ff3800", code_generator: "WHATSAPP_TEMPLATE_MESSAGE" do
  ref_Template_ff3800 =
    send_message_template(
      "mensageria_confirmacao_coeq_v1",
      "pt_BR",
      [
        "@contact.name ",
        "@contact.equipe_nome ",
        "@contact.estabelecimento_nome ",
        "@contact.estabelecimento_telefone ",
        "@contact.horario_funcionamento ",
        "@contact.estabelecimento_endereco ",
        "@contact.estabelecimento_documentos "
      ],
      buttons: ["CONFIRMO!", "AJUSTAR INFORMAÇÕES", "OUTROS"]
    )

  then(Informacoes_inicio_confirmadas when ref_Template_ff3800.index == 0)
  then(Ajustar_info_inicio when ref_Template_ff3800.index == 1)
  then(Buttons_9f109d when ref_Template_ff3800.index == 2)
end

```

<!-- { section: "dfdffea4-30f1-4ba4-b280-68214cd5fac9", x: 6672, y: 2112} -->

```stack
card Insight_9e6067, "Insight_9e6067", code_generator: "WRITE_RESULTS" do
  write_result("Confirmou", "concluido")
  then(Obrigado_pelas_info_ee6f35_3765f0_ace2e4)
end

```

<!-- { section: "ee2cf5c5-6da7-4ee7-b3ba-2d933c81ad50", x: -600, y: 0} -->

```stack
card Insight_1dde8f, "Insight_1dde8f", code_generator: "WRITE_RESULTS" do
  write_result("municipio", "@Contact.municipio")
  then(Branch_8121a5)
end

```

<!-- { section: "1197dcec-9d99-4431-8564-02c1b6c8d3a6", x: 2256, y: 2016} -->

```stack
card Buttons_1f4682, "Buttons_1f4682", code_generator: "REPLY_BUTTON_TEXT" do
  ref_Buttons_1f4682 =
    buttons(["Button 1"]) do
      text(
        "Aqui está o exemplo da mensagem que será enviado para o usuário de saúde da sua Unidade de Saúde:

🚨 *Você sabia que com um de exame 20 minutos você pode detectar precocemente o câncer de colo do útero?*

Olá *{{NOME}}*! Aqui é a Secretaria de Saúde de *{{MUNICIPIO}}*, e de acordo com seu prontuário de saúde, *você está há mais de 2 anos sem coletar seu exame preventivo/ papanicolau.*
Este exame é oferecido *gratuitamente pelo SUS*, e sua unidade de saúde está pronta para realizar a coleta.

Apesar de ser o terceiro câncer que mais mata mulheres no Brasil, quando as lesões são detectadas cedo, as chances de cura aumentam em 100%!

*Não subestime a importância desse acompanhamento regular, sua saúde agradece!*"
      )
    end

  then(RESERVED_DEFAULT_CARD when ref_Buttons_1f4682 == "Button 1")
end

```

<!-- { section: "0d3780ec-e7cd-4db8-b8f9-fab6ffe1134a", x: 2424, y: 1824} -->

```stack
card HANDOVER_STARTS_a48888, "HANDOVER_STARTS_a48888", code_generator: "HANDOVER_STARTS" do
  send_content("a3894d02-e558-32cd-aa24-6039e1f5de90", true)
  then(HANDOVER_HOLD_2e68a3)
end

card HANDOVER_HOLD_2e68a3, "HANDOVER_HOLD_2e68a3", code_generator: "HANDOVER_HOLD" do
  send_content("754b79a0-307c-96a9-9776-1b2ef098e3ce")
  add_label("Requested help")
  add_label("Situação Outros")
end

```

<!-- { section: "28287684-61d7-456b-be90-306041cc1cac", x: 1784, y: 1020} -->

```stack
card Inicia_situacao_outros, "Inicia_situacao_outros", code_generator: "HANDOVER_STARTS" do
  send_content("bb3d7d1e-53de-c64a-1572-9c808e9dd995", true)
  then(HANDOVER_HOLD_5ef3c6)
end

card HANDOVER_HOLD_5ef3c6, "HANDOVER_HOLD_5ef3c6", code_generator: "HANDOVER_HOLD" do
  send_content("dc454332-f6d7-16ee-704e-942e0573e202")
  add_label("Requested help")
  add_label("Situação Outros")

  then(
    Font_styleverticalalign_inheritfont_styleverticalalign_inheritNao_sou_desta_unidadefontfont
  )
end

```

<!-- { section: "3a7a133a-bfbe-4707-833e-621d9d0a3b06", x: -1000, y: 0} -->

```stack
card RESERVED_DEFAULT_CARD, "RESERVED_DEFAULT_CARD", code_generator: "RESERVED_DEFAULT_CARD" do
  # RESERVED_DEFAULT_CARD
end

```