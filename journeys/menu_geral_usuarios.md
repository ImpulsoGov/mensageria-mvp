<!-- { section: "038a3cba-137c-47ad-adf7-f02147720469", x: 0, y: 0} -->

```stack
trigger(on: "CATCH ALL")

```

<!-- { section: "4072f3e0-f3e4-4957-8a22-2f1d0acee2b8", x: 500, y: 0} -->

```stack
card Text_1, "Text_1", code_generator: "TEXT_MESSAGE" do
  text(
    "Esse número pertence a Secretaria de @contact.municipio. Neste momento estamos utilizando ele apenas para campanhas automatizadas de saúde, ainda não conseguimos responder individualmente. Procure sua unidade de referência para questionamentos."
  )
end

```

<!-- { section: "a1a22853-25b5-4757-bb4f-bd8293ceb382", x: -1000, y: 0} -->

```stack
card RESERVED_DEFAULT_CARD, "RESERVED_DEFAULT_CARD", code_generator: "RESERVED_DEFAULT_CARD" do
  # RESERVED_DEFAULT_CARD
end

```