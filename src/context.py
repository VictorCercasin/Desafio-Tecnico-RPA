"""Estado compartilhado de uma execução do robô."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class RuntimeContext:
    hora_execucao: str | None = None
    data_atual: str | None = None
    resultados_dir: Path | None = None
    assets_dir: Path | None = None
    base_dir: Path | None = None

    def init_defaults(self, base_dir: Path, path_fakturama_exe: Path, now: datetime | None = None) -> None:
        """Inicializa uma nova execução; `now` permite testes determinísticos."""
        if now is None:
            now = datetime.now()

        self.hora_execucao = now.strftime("%H:%M:%S")
        self.data_atual = now.strftime("%d/%m/%Y")
        self.path_fakturama_exe = path_fakturama_exe

        # Evita caracteres inválidos em nomes de pastas no Windows.
        id_execucao = now.strftime("%Y-%m-%d_%H-%M-%S_%f")
        self.base_dir = base_dir
        self.resultados_dir = Path(base_dir) / "resultados" / id_execucao
        self.resultados_dir.mkdir(parents=True, exist_ok=False)
        self.assets_dir = Path(base_dir) / "assets"


    def caminho_resultado(self, nome_arquivo: str) -> Path:
        if self.resultados_dir is None:
            raise RuntimeError("CTX não foi inicializado; chame CTX.init_defaults() no main.")
        return self.resultados_dir / nome_arquivo

    @property
    def comprador_csv(self) -> Path:
        return self.caminho_resultado("comprador.csv")

    @property
    def catalogo_csv(self) -> Path:
        return self.caminho_resultado("catalogo.csv")

    @property
    def print_comprador(self) -> Path:
        return self.caminho_resultado("cadastro_comprador.png")

    @property
    def print_catalogo(self) -> Path:
        return self.caminho_resultado("lista_produtos.png")

    @property
    def log_file(self) -> Path:
        return self.caminho_resultado("exec.log")


CTX = RuntimeContext()
