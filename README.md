# Desafio técnico — Coleta web e cadastro no Fakturama

Automação em Python que coleta um comprador fictício no Fake Name Generator e o catálogo do Sauce Demo, gera arquivos CSV e cadastra os dados no Fakturama por interação com a interface gráfica.

Além de atender ao desafio, a implementação demonstra práticas aplicáveis a automações mais complexas, como separação de responsabilidades, validação de dados, registro de evidências e controle de progresso para retentativas.

## Fluxo

1. Inicializa uma pasta exclusiva para a execução e configura o log.
2. Coleta nome, sobrenome e CEP do comprador.
3. Acessa o Sauce Demo e coleta número, nome, descrição e preço dos produtos.
4. Valida os dados com Pydantic e grava os CSVs.
5. Abre o Fakturama, aguarda sua interface e cadastra os registros pendentes.
6. Atualiza o status de cada cadastro no CSV e captura as telas do comprador e do catálogo.
7. Encerra o processo do Fakturama e informa o resultado da execução.

A coleta web usa Selenium e BeautifulSoup. O cadastro desktop usa reconhecimento de imagens, navegação por teclado e colagem de texto pela área de transferência.

## Pré-requisitos

- Windows com sessão gráfica ativa e desbloqueada.
- Python 3.14, versão utilizada no desenvolvimento.
- Google Chrome instalado.
- Fakturama 2 instalado, com a configuração inicial concluída e o ambiente de trabalho pronto para uso.
- Conexão com a internet para acessar os sites e, quando necessário, resolver o ChromeDriver pelo Selenium Manager.
- Dependências Python relacionadas em `requirements.txt`.

O projeto usa Selenium, BeautifulSoup, Pydantic, Colorlog, PyAutoGUI, Pyperclip, Pillow e PyWin32. O reconhecimento com `confidence` também requer OpenCV. As dependências e suas versões são instaladas pelo arquivo `requirements.txt`.

### Interface e tela

A execução de referência foi realizada em **1920 × 1080**, com o Fakturama maximizado, interface em inglês e configuração de país/moeda brasileira.

Os modelos de imagem estão em `assets/`. Resolução, escala de exibição do Windows, tema e idioma podem alterar o reconhecimento. O percentual de escala utilizado na execução de referência não foi registrado; se as imagens não forem reconhecidas, ajuste a configuração de exibição ou recapture os modelos no ambiente de destino.

Mantenha o Fakturama visível e feche instâncias abertas antes de iniciar. Durante a execução, evite usar mouse, teclado ou área de transferência e não bloqueie a sessão. O robô depende do foco e da disposição dos campos para navegar com Tab.

## Instalação

Abra o PowerShell na pasta do projeto e execute:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Os comandos usam diretamente o Python do ambiente virtual, sem exigir sua ativação. O arquivo `start_env.bat` é uma alternativa para abrir um terminal com a `.venv` já ativada; ele não instala dependências nem executa o robô.

## Execução

Com o Fakturama fechado:

```powershell
.\.venv\Scripts\python.exe main.py
```

O caminho padrão do executável, definido em `src/settings.py`, é:

```text
C:\Program Files\Fakturama2\Fakturama.exe
```

Para informar outro caminho:

```powershell
.\.venv\Scripts\python.exe main.py -p "D:\Aplicativos\Fakturama2\Fakturama.exe"
```

A opção longa equivalente é `--fakturama-exe`. Para consultar a ajuda:

```powershell
.\.venv\Scripts\python.exe main.py --help
```

O programa retorna código de saída **0** em caso de sucesso e código diferente de zero em caso de falha. As URLs dos sites também são configuradas em `src/settings.py`.

## Resultados

Cada execução cria uma pasta em `resultados/`, identificada por data, hora e microssegundos. Os arquivos são:

| Arquivo | Conteúdo |
|---|---|
| `comprador.csv` | Nome, sobrenome, CEP e status do comprador |
| `catalogo.csv` | Número, nome, descrição, preço e status de cada produto |
| `exec.log` | Etapas da execução, dados coletados, cadastros e falhas |
| `print_comprador.png` | Captura da janela do Fakturama com o comprador |
| `print_catalogo.png` | Captura da janela do Fakturama com a lista de produtos |
| `screenshots/` | Capturas de erro, quando ocorrem falhas e a captura é possível |

Os CSVs usam vírgula como delimitador e UTF-8 com BOM. O CEP é mantido como texto pelo robô; ao importar o arquivo em uma planilha, configure essa coluna como texto para preservar zeros iniciais.

O preço permanece com ponto decimal no CSV, por exemplo `29.99`. Na interface do Fakturama, o robô cola `29,99`, pois a colagem com ponto foi interpretada como separador de milhar no ambiente testado.

Os números dos produtos são os identificadores extraídos do Sauce Demo, incluindo o número zero. Os valores numéricos coletados são preservados, **sem conversão cambial**; o Fakturama os exibe na moeda configurada no aplicativo.

## Retentativas e status

Os dois CSVs possuem a coluna `status`:

| Status | Comportamento |
|---|---|
| `coletado` | O registro está pendente de cadastro |
| `cadastrado` | O fluxo de salvamento foi executado; o registro é pulado nas próximas tentativas |

O fluxo de cadastro possui até três tentativas por padrão. Em caso de falha, registra o erro, tenta capturar a tela, encerra o processo e inicia outra tentativa. Os CSVs são relidos para pular os registros já marcados. A coleta e a geração inicial dos arquivos ficam fora desse loop.

Cada atualização de status é escrita em um arquivo temporário e depois substitui o CSV original, reduzindo o risco de truncar o arquivo durante a escrita.

### Limitações da recuperação


- A recuperação ocorre entre tentativas da **mesma execução**. Executar `main.py` novamente cria outra pasta, coleta novos dados e não retoma automaticamente os arquivos anteriores.
- Não há busca automática por compradores ou produtos já existentes no Fakturama. Use um ambiente de teste e controle os cadastros anteriores ao repetir execuções.


## Organização do código

| Arquivo ou pasta | Responsabilidade |
|---|---|
| `main.py` | Argumentos de execução e coordenação das etapas |
| `src/context.py` | Caminhos e contexto da execução |
| `src/settings.py` | URLs e caminho padrão do Fakturama |
| `src/config_logger.py` | Log em arquivo e console |
| `src/schemas.py` | Modelos e validação dos dados |
| `src/fakenamegenerator.py` | Coleta do comprador |
| `src/saucedemo.py` | Login e coleta do catálogo |
| `src/csv.py` | Gravação dos CSVs e atualização de status |
| `src/fakturama.py` | Abertura, cadastro e encerramento do Fakturama |
| `src/utils/driver.py` | Configuração e interações do navegador |
| `src/utils/imagens.py` | Localização, espera e clique por imagem |
| `src/utils/utils.py` | Capturas de tela e maximização da janela |
| `assets/` | Imagens de referência da interface |



## Diagnóstico de falhas

Consulte primeiro o traceback em `exec.log` e as capturas disponíveis em `screenshots/`.

| Sintoma | Verificação |
|---|---|
| Executável não encontrado | Confira o caminho padrão ou informe `-p` |
| Imagem não encontrada | Confira os modelos em `assets/`, resolução, escala, idioma, janela visível e ausência de diálogos |
| Texto inserido no campo errado | Confira o foco inicial e a sequência de Tab no formulário |
| Falha ao iniciar Chrome | Confira a instalação do navegador, acesso à rede e o erro do Selenium Manager |
| Preço multiplicado por 100 | Confira se o texto colado no campo usa vírgula decimal |
| Falha ao capturar a janela | Confira se o processo continua ativo, a janela está disponível e Pillow está instalado com suporte ao argumento `window` |

Para alterações de interface, atualize as imagens de referência e valide novamente um cadastro completo antes de executar o catálogo inteiro.
