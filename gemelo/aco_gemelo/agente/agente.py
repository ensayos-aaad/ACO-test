"""El agente (hormiga) del gemelo.

Es un **programa de agente** en el sentido de Russell & Norvig: recibe un percepto y
devuelve una acción. No conoce el mundo ni la meta; solo ve su celda y las 8 vecinas
(mensaje PERCEPCION), y habla con los demás únicamente por el canal. ``paso()`` no bloquea:
es el equivalente del ``loop()`` de un microcontrolador.

Ciclo de vida (DECISIONES-PRUEBA.md, D3, I4 e I5; depósito a la vuelta, como en S-ACO):

1. **IDA**: explora sin depositar y guarda su ruta, sin bucles, en una memoria de K movimientos.
2. Al llegar a la meta avisa a la madre (DANZA) y pasa a **VOLVIENDO**: desanda su ruta
   depositando feromona.
3. En el nido, si le faltan viajes (``viajes``, decisión J2), vuelve a explorar desde cero
   con la feromona que ya hay; si no, pasa a **SIGUIENDO**: recorre de nuevo su ruta hasta la meta.
4. En la meta queda **ASENTADA**.

Si la memoria se llena antes de encontrar la meta, hace un **RETROCESO** al nido por su
propia ruta, sin depositar, y empieza de nuevo.

Con una madre presente (artefacto 7) el agente además:

- informa su mapa por bloques (FRAGMENTO) si ``informa_mapa`` está activo;
- ante un RECLUTA elige una ruta anunciada, vuelve al nido, la pide (PIDE_RUTA) y espera;
- ante una RUTA (pedida, de rescate o difundida) vuelve al nido, la recorre hasta la meta,
  regresa depositando sobre ella y vuelve a la meta para quedarse;
- ante un MAPA, al explorar prefiere las celdas que la colonia todavía no conoce.

Aún no implementado: BALIZA, ALERTA, SIGUEME y STOP.

La **verificadora** no explora: en cada paso va a la vecina no visitada con más feromona.
Si se queda sin rastro, queda **FALLIDA**.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..canal import Canal
from ..mundo.mundo import DIRECCIONES, Celda, Clase
from ..protocolo import (
    FLAG_ACK,
    FLAG_RESCATE,
    FLAG_VERIFICACION,
    ID_MADRE,
    ID_MUNDO,
    byte_a_celda,
    celda_a_byte,
    celdas_a_bloque,
    crear,
    nombre_de,
)

#: Direcciones ortogonales que toca cada diagonal (para no cortar esquinas).
_ORTOGONALES = {4: (0, 1), 5: (1, 2), 6: (2, 3), 7: (3, 0)}
_DIRECCION_DE = {d: i for i, d in enumerate(DIRECCIONES)}


#: Qué hace una agente con una RUTA de la madre ("usado" o el motivo para ignorarla).
MOTIVOS_RUTA = ("usado", "ya_llego", "ya_tiene_ruta", "fallida", "ocupada", "no_cabe",
                "otro_nido", "verificadora")


class Estado(Enum):
    """Estado interno del agente. El valor es el código ``estado`` que viaja en el protocolo."""

    IDA = 0
    VOLVIENDO = 1
    SIGUIENDO = 2
    ASENTADA = 2
    RETROCESO = 0
    ESPERANDO = 0
    FALLIDA = 3

    # Estados con el mismo código de protocolo deben seguir siendo distintos entre sí.
    def __new__(cls, codigo: int):
        obj = object.__new__(cls)
        obj._value_ = len(cls.__members__)
        obj.codigo = codigo
        return obj


@dataclass
class ConfigAgente:
    """Parámetros del agente (valores por defecto: DECISIONES-PRUEBA.md, sección I).

    Attributes:
        alpha: exponente de la feromona (I1).
        k: atractivo de una celda sin feromona; hace el papel de τ₀ (I2). La regla de
            elección es ``(k + nivel)^alpha``, con ``nivel`` = feromona percibida (0–15).
        theta: umbral de cambio de rol (I8). Con 0 el agente siempre explota.
        K: memoria, en movimientos de su ruta (I9).
        deposito: ``"calidad"`` (255 / largo de la ruta) o ``"constante"`` (I6).
        deposito_valor: unidades que deposita por celda en el modo constante.
        delta_t: cada cuántos ticks informa su ESTADO a la madre.
        con_madre: si hay una madre a la que informar.
        verificadora: si es la agente verificadora.
        informa_mapa: si envía a la madre lo que descubre del mapa (FRAGMENTO).
        viajes: idas y vueltas con depósito antes de asentarse (J2). Con 1, se asienta tras
            la primera vuelta.
    """

    alpha: float = 2.0
    k: float = 1.0
    theta: float = 8.0
    K: int = 64
    deposito: str = "calidad"
    deposito_valor: int = 1
    delta_t: int = 10
    con_madre: bool = True
    verificadora: bool = False
    informa_mapa: bool = False
    viajes: int = 1


def prob_explotar(s: int, theta: float) -> float:
    """Probabilidad de actuar como explotadora ante un estímulo ``s`` (umbral de respuesta).

    ``P = s² / (s² + θ²)`` (Bonabeau, Theraulaz y Deneubourg, 1996). Con ``θ = 0`` vale 1.
    """
    if theta == 0:
        return 1.0
    return s * s / (s * s + theta * theta)


class Agente:
    """Una hormiga: decide con lo que percibe y se comunica solo por el canal."""

    def __init__(self, id_agente: int, canal: Canal, config: ConfigAgente | None = None,
                 semilla: int = 0) -> None:
        self.id = id_agente
        self.canal = canal
        self.config = config or ConfigAgente()
        self.rng = random.Random(semilla * 256 + id_agente)
        self.estado = Estado.IDA
        self.rol = 0  #: 0 = exploradora · 1 = explotadora (el del último paso)
        self.pos: Celda | None = None
        self.ruta: list[Celda] = []  #: del nido a la celda actual, sin bucles
        self.visitadas: set[Celda] = set()  #: celdas pisadas en este viaje (un mapa de bits en el micro)
        self._previa: Celda | None = None  #: celda de la que viene
        self.indice = 0  #: posición dentro de la ruta al volver o al seguirla
        self.llegadas = 0
        self.reinicios = 0  #: veces que se le llenó la memoria
        self.viajes_hechos = 0  #: idas y vueltas completas (con depósito)
        #: Contadores de mecanismos (C4): lo que realmente pasó, no lo que se infiere del resultado.
        self.rescates: dict[str, int] = {}  #: rescates recibidos, por lo que se hizo con ellos
        self.rutas_pedidas = 0  #: PIDE_RUTA enviados (reclutamiento aceptado)
        self.rutas_heredadas = 0  #: rutas de la madre adoptadas (pedidas o de rescate)
        self.rutas_ignoradas: dict[str, int] = {}  #: RUTA que no son de rescate y no se usaron, por motivo
        self.entradas: list[Celda] = []  #: primera celda tras el nido de cada ruta que llegó a la meta
        self.conocidas: set[Celda] = set()  #: celdas observadas (un mapa de bits en el micro)
        self.obstaculos: set[Celda] = set()  #: obstáculos observados
        self.mapa_colonia: set[Celda] = set()  #: celdas que la colonia conoce (según la madre)
        self.terminado = False
        self.rescatada = False
        self._ahora = 0
        self._al_nido = "reiniciar"  #: qué hacer al terminar un RETROCESO
        self._ruta_pedida: int | None = None
        self._ruta_heredada: list[Celda] | None = None
        self._debe_vuelta = False  #: llegó por una ruta heredada y aún no la reforzó
        self._espera_desde = 0
        self._reportadas: set[Celda] = set()
        self._seq = 0
        self._ultimo_estado = None
        canal.registrar(id_agente)

    # ------------------------------------------------------------------ ciclo no bloqueante

    def paso(self, ahora: int) -> None:
        """Un ciclo: lee lo que llegó, decide si hay un percepto nuevo e informa a la madre."""
        percepto = None
        for msg in self.canal.recibir(self.id):
            nombre = nombre_de(msg)
            if nombre == "PERCEPCION":
                percepto = msg
            elif nombre == "RECLUTA":
                self._reclutar(msg)
            elif nombre == "RUTA":
                self._heredar(msg)
            elif nombre == "MAPA":
                ancho = self.canal.ctx.ancho  # type: ignore[attr-defined]
                self.mapa_colonia = {(i % ancho, i // ancho)
                                     for i, bit in enumerate(msg["conocidas"]) if bit}
            elif nombre == "FIN":
                self.terminado = True
        if self.terminado or percepto is None:
            return
        self._ahora = ahora
        accion = self.decidir(percepto, ahora)
        self._enviar("ACCION", ID_MUNDO, ahora, **accion)
        cfg = self.config
        if cfg.con_madre and (self._ultimo_estado is None or ahora - self._ultimo_estado >= cfg.delta_t):
            self._ultimo_estado = ahora
            # La verificadora marca su ESTADO para que la madre no la cuente como parte de la
            # colonia (F-020: la tomaba por rezagada y la rescataba).
            self._enviar("ESTADO", ID_MADRE, ahora,
                         flags=FLAG_VERIFICACION if cfg.verificadora else 0, pos=celda_a_byte(self.pos),
                         estado=self.codigo_estado, rol=self.rol,
                         experiencia=min(255, len(self.conocidas)), llegadas=min(255, self.llegadas))
            if cfg.informa_mapa:
                self._informar_mapa(ahora)

    @property
    def codigo_estado(self) -> int:
        """Código ``estado`` del protocolo (3 mientras recorre una ruta de rescate)."""
        if self.rescatada and self.estado in (Estado.SIGUIENDO, Estado.VOLVIENDO):
            return 3
        return self.estado.codigo

    # ------------------------------------------------------------------ programa de agente

    def decidir(self, percepto: dict[str, Any], ahora: int = 0) -> dict[str, int]:
        """Percepto → acción. Devuelve los campos del mensaje ACCION."""
        vecinas = percepto["vecinas"]
        self._actualizar_posicion(byte_a_celda(percepto["pos"]), vecinas)
        if self.estado in (Estado.ASENTADA, Estado.FALLIDA):
            return _quieto()
        if self.estado is Estado.ESPERANDO:
            if ahora - self._espera_desde > 3 * self.config.delta_t:  # la ruta no llegó
                self._ruta_pedida = None
                self.estado = Estado.IDA
            else:
                return _quieto()
        en_meta = vecinas[0]["clase"] == Clase.META
        if self.estado is Estado.IDA:
            if en_meta:
                return self._llegar(ahora)
            if len(self.ruta) - 1 >= self.config.K:
                self.estado = Estado.RETROCESO
                self.indice = len(self.ruta) - 1
            else:
                direccion = self._elegir_verificadora(vecinas) if self.config.verificadora \
                    else self.elegir(vecinas)
                if direccion is None:
                    return self._fallar(ahora)
                return _mover(direccion)
        if self.estado is Estado.RETROCESO:
            if self.indice == 0:
                return self._en_el_nido(percepto, ahora)
            return _mover(self._hacia(self.ruta[self.indice - 1]))
        if self.estado is Estado.VOLVIENDO:
            if self.indice == 0:
                self.viajes_hechos += 1
                if self.viajes_hechos < self.config.viajes:  # otro viaje: explora de nuevo
                    self.ruta = [self.pos]
                    self.visitadas = {self.pos}
                    self._previa = None
                    self.estado = Estado.IDA
                else:
                    self.estado = Estado.SIGUIENDO
                return self.decidir(percepto, ahora)
            return _mover(self._hacia(self.ruta[self.indice - 1]), self._deposito())
        # SIGUIENDO: recorre su ruta hasta la meta.
        if self.indice == len(self.ruta) - 1:
            self.llegadas += 1
            if self._debe_vuelta and self.indice > 0:  # refuerza la ruta heredada
                self._debe_vuelta = False
                self.estado = Estado.VOLVIENDO
                return _mover(self._hacia(self.ruta[self.indice - 1]), self._deposito())
            self.estado = Estado.ASENTADA
            return _quieto()
        return _mover(self._hacia(self.ruta[self.indice + 1]))

    def movimientos_validos(self, vecinas: list[dict[str, int]]) -> list[int]:
        """Direcciones a las que se puede ir según lo percibido (sin cortar esquinas)."""
        def libre(d: int) -> bool:
            return vecinas[1 + d]["clase"] in (Clase.LIBRE, Clase.META)

        return [
            d for d in range(8)
            if libre(d) and all(libre(o) for o in _ORTOGONALES.get(d, ()))
        ]

    def elegir(self, vecinas: list[dict[str, int]]) -> int | None:
        """Regla de decisión de la hormiga en la IDA. Devuelve una dirección.

        Si ve la meta al lado, va a ella. Si no, como en S-ACO, prefiere las celdas que no ha
        pisado en este viaje; si ya las pisó todas, evita solo la celda de la que acaba de llegar
        (así sale de un callejón por donde entró). Entre esas candidatas sortea su rol con el
        umbral de respuesta y elige: la explotadora con probabilidad proporcional a
        ``(k + nivel)^alpha``; la exploradora al azar, prefiriendo celdas que la colonia no conoce.
        """
        validos = self.movimientos_validos(vecinas)
        if not validos:
            return None
        for d in validos:
            if vecinas[1 + d]["clase"] == Clase.META:
                return d
        nuevos = [d for d in validos
                  if self._destino(d) not in self.visitadas and self._destino(d) not in self.ruta]
        candidatos = nuevos or [d for d in validos if self._destino(d) != self._previa] or validos
        cfg = self.config
        niveles = [vecinas[1 + d]["fero"] for d in candidatos]
        self.rol = int(self.rng.random() < prob_explotar(max(niveles), cfg.theta))
        if self.rol:
            pesos = [(cfg.k + nivel) ** cfg.alpha for nivel in niveles]
            if sum(pesos) > 0:
                return self.rng.choices(candidatos, weights=pesos)[0]
        sin_explorar = [d for d in candidatos if self._destino(d) not in self.mapa_colonia]
        return self.rng.choice(sin_explorar or candidatos)

    def _elegir_verificadora(self, vecinas: list[dict[str, int]]) -> int | None:
        """La verificadora solo explota: va a la vecina no visitada con más feromona.

        Los empates se resuelven al azar. Devuelve ``None`` si no queda rastro que seguir.
        """
        self.rol = 1
        validos = self.movimientos_validos(vecinas)
        for d in validos:
            if vecinas[1 + d]["clase"] == Clase.META:
                return d
        nuevos = [d for d in validos if self._destino(d) not in self.ruta]
        mejor = max((vecinas[1 + d]["fero"] for d in nuevos), default=0)
        if mejor == 0:
            return None
        return self.rng.choice([d for d in nuevos if vecinas[1 + d]["fero"] == mejor])

    # ------------------------------------------------------------------ interno

    def _actualizar_posicion(self, pos: Celda, vecinas: list[dict[str, int]]) -> None:
        """Registra dónde está (el mundo es la autoridad) y lo que ve."""
        if self.pos is not None and self.pos != pos:
            self._previa = self.pos
        self.pos = pos
        self.conocidas.add(pos)
        for d, (dx, dy) in enumerate(DIRECCIONES):
            if vecinas[1 + d]["clase"] != Clase.FUERA:
                self.conocidas.add((pos[0] + dx, pos[1] + dy))
            if vecinas[1 + d]["clase"] == Clase.OBSTACULO:
                self.obstaculos.add((pos[0] + dx, pos[1] + dy))
        if self.estado is Estado.IDA:
            self.visitadas.add(pos)
            if pos in self.ruta:
                del self.ruta[self.ruta.index(pos) + 1:]  # cierra el bucle: la ruta sigue sin repetir
            else:
                self.ruta.append(pos)
        elif self.estado in (Estado.VOLVIENDO, Estado.RETROCESO, Estado.SIGUIENDO):
            if pos not in self.ruta:  # el último movimiento de la IDA se confirmó después del cambio
                self.ruta.append(pos)
            self.indice = self.ruta.index(pos)

    def _en_el_nido(self, percepto: dict[str, Any], ahora: int) -> dict[str, int]:
        """Terminó un RETROCESO: adopta la ruta heredada, pide la anunciada o empieza de nuevo."""
        motivo, self._al_nido = self._al_nido, "reiniciar"
        heredada, self._ruta_heredada = self._ruta_heredada, None
        if motivo == "adoptar" and heredada and heredada[0] == self.pos:
            self.ruta = heredada
            self.indice = 0
            self._debe_vuelta = True
            self.estado = Estado.SIGUIENDO
            return self.decidir(percepto, ahora)
        self.ruta = [self.pos]
        self.visitadas = {self.pos}
        self._previa = None
        if motivo == "pedir" and self._ruta_pedida is not None:
            self._enviar("PIDE_RUTA", ID_MADRE, ahora, flags=FLAG_ACK, ruta_id=self._ruta_pedida)
            self.rutas_pedidas += 1
            self._espera_desde = ahora
            self.estado = Estado.ESPERANDO
            return _quieto()
        if motivo == "reiniciar":
            self.reinicios += 1
        self.rescatada = False
        self.estado = Estado.IDA
        return self.decidir(percepto, ahora)

    def _disponible(self) -> bool:
        """Si todavía busca la meta y puede aceptar ayuda de la madre."""
        return (not self.config.verificadora and self.llegadas == 0
                and self._ruta_heredada is None
                and self.estado in (Estado.IDA, Estado.RETROCESO, Estado.ESPERANDO))

    def _volver_al_nido(self, motivo: str) -> None:
        self._al_nido = motivo
        self.estado = Estado.RETROCESO
        self.indice = len(self.ruta) - 1

    def _reclutar(self, msg: dict[str, Any]) -> None:
        """RECLUTA: elige una ruta anunciada (según su peso) y vuelve al nido a pedirla."""
        if not self._disponible() or self._ruta_pedida is not None or not msg["rutas"]:
            return
        pesos = [ruta["peso"] or 1 for ruta in msg["rutas"]]
        self._ruta_pedida = self.rng.choices(msg["rutas"], weights=pesos)[0]["ruta_id"]
        self._volver_al_nido("pedir")

    def _heredar(self, msg: dict[str, Any]) -> None:
        """RUTA de la madre: la guarda y vuelve al nido para recorrerla."""
        rescate = bool(msg["flags"] & FLAG_RESCATE)
        motivo = self._motivo_para_ignorar(msg)
        if rescate:
            self.rescates[motivo or "usado"] = self.rescates.get(motivo or "usado", 0) + 1
        if motivo:
            if not rescate:
                self.rutas_ignoradas[motivo] = self.rutas_ignoradas.get(motivo, 0) + 1
            return
        celdas = [byte_a_celda(msg["inicio"])]
        for d in msg["movs"]:
            celdas.append((celdas[-1][0] + DIRECCIONES[d][0], celdas[-1][1] + DIRECCIONES[d][1]))
        self.rutas_heredadas += 1
        self._ruta_heredada = celdas
        self.rescatada = bool(msg["flags"] & FLAG_RESCATE)
        self._volver_al_nido("adoptar")

    def _motivo_para_ignorar(self, msg: dict[str, Any]) -> str | None:
        """Por qué no se puede usar una RUTA de la madre, o ``None`` si se puede."""
        if self.config.verificadora:
            return "verificadora"
        if self.llegadas > 0:
            return "ya_llego"
        if self._ruta_heredada is not None:
            return "ya_tiene_ruta"
        if self.estado is Estado.FALLIDA:
            return "fallida"
        if not self._disponible():
            return "ocupada"
        if msg["largo"] > self.config.K or not self.ruta:
            return "no_cabe"
        if byte_a_celda(msg["inicio"]) != self.ruta[0]:
            return "otro_nido"
        return None

    def _informar_mapa(self, ahora: int) -> None:
        """Envía a la madre un bloque de 4 × 4 con celdas que aún no le había informado."""
        pendientes = self.conocidas - self._reportadas
        if not pendientes:
            return
        x, y = min(pendientes, key=lambda c: (c[1] // 4, c[0] // 4))
        origen = (x - x % 4, y - y % 4)
        self._enviar("FRAGMENTO", ID_MADRE, ahora, origen=celda_a_byte(origen),
                     conocidas=celdas_a_bloque(origen, self.conocidas),
                     obstaculos=celdas_a_bloque(origen, self.obstaculos))
        self._reportadas |= {c for c in self.conocidas
                             if (c[0] - c[0] % 4, c[1] - c[1] % 4) == origen}

    def _llegar(self, ahora: int) -> dict[str, int]:
        """Llegó a la meta: avisa a la madre y empieza a volver (la verificadora se queda)."""
        self.llegadas += 1
        if len(self.ruta) > 1:
            self.entradas.append(self.ruta[1])
        flags = FLAG_ACK | (FLAG_VERIFICACION if self.config.verificadora else 0)
        if self.config.con_madre:
            movs = [self._direccion(a, b) for a, b in zip(self.ruta, self.ruta[1:])]
            self._enviar("DANZA", ID_MADRE, ahora, flags=flags, ruta_id=self.llegadas % 256,
                         inicio=celda_a_byte(self.ruta[0]), largo=len(movs), movs=movs)
        if self.config.verificadora:
            self.estado = Estado.ASENTADA
            return _quieto()
        self.estado = Estado.VOLVIENDO
        self.indice = len(self.ruta) - 1
        if self.indice == 0:
            return _quieto()
        return _mover(self._hacia(self.ruta[self.indice - 1]), self._deposito())

    def _fallar(self, ahora: int) -> dict[str, int]:
        """Sin salida (o, para la verificadora, sin rastro): queda FALLIDA y avisa."""
        self.estado = Estado.FALLIDA
        if self.config.con_madre:
            flags = FLAG_ACK | (FLAG_VERIFICACION if self.config.verificadora else 0)
            self._enviar("PIDE_RESCATE", ID_MADRE, ahora, flags=flags,
                         experiencia=min(255, len(self.conocidas)), motivo=1)
        return _quieto()

    def _deposito(self) -> int:
        cfg = self.config
        if cfg.deposito == "constante":
            return cfg.deposito_valor
        return max(1, min(255, round(255 / max(1, len(self.ruta) - 1))))

    def _destino(self, direccion: int) -> Celda:
        dx, dy = DIRECCIONES[direccion]
        return (self.pos[0] + dx, self.pos[1] + dy)

    def _hacia(self, celda: Celda) -> int:
        return self._direccion(self.pos, celda)

    @staticmethod
    def _direccion(origen: Celda, destino: Celda) -> int:
        return _DIRECCION_DE[(destino[0] - origen[0], destino[1] - origen[1])]

    def _enviar(self, nombre: str, dst: int, ahora: int, flags: int = 0, **campos: Any) -> None:
        self.canal.enviar(crear(nombre, src=self.id, dst=dst, seq=self._seq, tick=ahora % 65536,
                                flags=flags, **campos))
        self._seq = (self._seq + 1) % 256


def _quieto() -> dict[str, int]:
    return {"accion": 0, "dir": 0, "deposito": 0}


def _mover(direccion: int, deposito: int = 0) -> dict[str, int]:
    return {"accion": 2 if deposito else 1, "dir": direccion, "deposito": deposito}
