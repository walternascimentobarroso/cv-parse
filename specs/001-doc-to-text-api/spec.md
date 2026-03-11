# Feature Specification: API de Documentos para Texto

**Feature Branch**: `001-doc-to-text-api`  
**Created**: 2026-03-10  
**Status**: Draft  
**Input**: User description: "uma api simples para ler documentos e transformar em textos"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enviar documento e receber texto (Priority: P1)

Um consumidor da API envia um documento (ficheiro) e recebe de volta o conteúdo em formato texto simples. O fluxo é: envio do documento → processamento → resposta com o texto extraído.

**Why this priority**: É o fluxo central da feature; sem ele não há valor entregue.

**Independent Test**: Enviar um documento válido e verificar que a resposta contém o texto esperado, sem necessidade de autenticação complexa ou outros fluxos.

**Acceptance Scenarios**:

1. **Given** um documento suportado, **When** o consumidor envia o documento para o endpoint designado, **Then** o sistema responde com o texto extraído em formato texto simples.
2. **Given** um documento vazio ou sem conteúdo extraível, **When** o consumidor envia o documento, **Then** o sistema responde com texto vazio ou indicação clara de que não há conteúdo.

---

### User Story 2 - Rejeitar formatos não suportados (Priority: P2)

O consumidor envia um tipo de ficheiro que o sistema não suporta e recebe uma resposta de erro clara, sem falha silenciosa.

**Why this priority**: Evita confusão e permite que integradores saibam o que é aceite.

**Independent Test**: Enviar um ficheiro com tipo não suportado e verificar que a resposta é um erro explícito (e opcionalmente lista de formatos suportados).

**Acceptance Scenarios**:

1. **Given** um ficheiro num formato não suportado, **When** o consumidor envia o documento, **Then** o sistema responde com erro indicando formato não suportado.
2. **Given** um pedido sem documento (corpo vazio ou ausente), **When** o consumidor faz o pedido, **Then** o sistema responde com erro indicando que o documento é obrigatório.

---

### User Story 3 - Limites de tamanho e resposta a falhas (Priority: P3)

Documentos excessivamente grandes são rejeitados; falhas de processamento resultam em mensagens de erro compreensíveis.

**Why this priority**: Protege o sistema e dá feedback útil em cenários de falha.

**Independent Test**: Enviar documento acima do limite ou que provoque falha e verificar que a resposta é um erro claro, não um crash ou resposta vazia ambígua.

**Acceptance Scenarios**:

1. **Given** um documento que excede o tamanho máximo permitido, **When** o consumidor envia o documento, **Then** o sistema responde com erro indicando o limite e que o documento foi rejeitado.
2. **Given** uma falha interna ao extrair texto (por exemplo, ficheiro corrompido), **When** o processamento falha, **Then** o sistema responde com erro genérico adequado ao consumidor, sem expor detalhes internos.

---

### Edge Cases

- O que acontece quando o documento tem apenas imagens (sem texto extraível)? O sistema deve responder com texto vazio ou mensagem explícita de que não foi possível extrair texto.
- O que acontece com caracteres especiais ou múltiplos idiomas? O texto devolvido deve preservar encoding de forma que o consumidor possa interpretar corretamente (por exemplo, UTF-8).
- Múltiplos ficheiros no mesmo pedido: assumir um único documento por pedido para manter a API simples; pedidos com múltiplos ficheiros podem ser rejeitados ou tratados como “apenas o primeiro”.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST expor um endpoint que aceite o envio de um documento (ficheiro) e devolva o conteúdo em texto simples.
- **FR-002**: O sistema MUST suportar pelo menos um formato de documento comum (por exemplo, PDF ou texto plano); formatos suportados devem ser documentados ou indicados na resposta de erro.
- **FR-003**: O sistema MUST rejeitar pedidos sem documento ou com corpo inválido, respondendo com erro claro.
- **FR-004**: O sistema MUST rejeitar documentos em formatos não suportados com mensagem de erro explícita.
- **FR-005**: O sistema MUST aplicar um limite máximo de tamanho de documento (valor definido na implementação) e rejeitar ficheiros que o excedam com erro claro.
- **FR-006**: Em caso de falha de processamento (ficheiro corrompido, erro interno), o sistema MUST responder com mensagem de erro adequada ao consumidor, sem expor stack traces ou detalhes internos.

### Key Entities

- **Documento (entrada)**: Ficheiro enviado pelo consumidor; tem tipo MIME/formato e tamanho; não é persistido além do tempo de processamento para manter a API simples.
- **Texto extraído (saída)**: Conteúdo em texto simples devolvido na resposta; encoding adequado (por exemplo, UTF-8) para suportar vários idiomas e caracteres especiais.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um consumidor consegue enviar um documento suportado e receber o texto extraído numa única chamada, com resposta em tempo aceitável (por exemplo, dentro de segundos para documentos de tamanho típico).
- **SC-002**: Pedidos com formato não suportado ou documento ausente recebem sempre uma resposta de erro explícita (não 200 com corpo vazio ou ambíguo).
- **SC-003**: Documentos até ao tamanho máximo configurado são processados com sucesso quando o formato é suportado e o conteúdo é extraível.
- **SC-004**: A API mantém contrato estável (endpoint e forma de envio/resposta) de forma a que integradores possam confiar no comportamento sem mudanças não documentadas.

## Assumptions

- “Documentos” incluem pelo menos um formato comum (por exemplo, PDF ou texto plano); o primeiro incremento pode suportar apenas um formato.
- A API é stateless: não é necessário guardar documentos ou resultados entre pedidos.
- Autenticação/autorização não são obrigatórias para o MVP; podem ser adicionadas depois (por exemplo, API key ou token) sem alterar o núcleo da funcionalidade.
- Consumidores são sistemas ou utilizadores que enviam ficheiros via HTTP (ou protocolo equivalente); não se assume interface gráfica de utilizador nesta especificação.
