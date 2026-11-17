"""Un ensayo completo: el mundo, la colonia, la madre y la verificadora.

Fases de un ensayo (decisiones D3, G1 e I11):

1. **Colonia**: las agentes buscan la meta hasta que todas quedan asentadas en ella.
2. **Verificación**: sale la verificadora desde el nido y sigue solo el rastro.
3. **Cierre**: se difunde FIN con el motivo.

Si se agota el límite de ticks antes de terminar, el ensayo se cierra como no convergido.

Hay dos motores que ejecutan **el mismo** ``paso()`` de cada actor:

- ``"determinista"``: un solo hilo, los actores en orden fijo. Con la misma semilla da siempre
  el mismo resultado. Es el de las pruebas y los experimentos.
- ``"hilos"``: un hilo por agente y otro para la madre, como si cada uno fuera un micro. El
  mundo espera la acción de cada agente antes de avanzar el tick (pregunta-respuesta, como en
  ``referencia/simulaciones/ejemplo5``). Es el de la demostración.

El motor mira el estado de las agentes directamente para saber cuándo cambiar de fase: es el
punto de vista del gemelo, que conoce la verdad. En el sistema real eso lo sabría la madre por
los mensajes ESTADO.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field, replace

from ..agente import Agente, ConfigAgente, Estado
from ..canal import CanalMemoria
from ..madre import ConfigMadre, Madre, Modo
from ..mundo import Mundo
from ..mundo.mundo import Celda
from ..protocolo import ID_DIFUSION, ID_MADRE, ID_MUNDO, Contexto, celda_a_byte, crear, nombre_de


@dataclass
class ConfigEnsayo:
    """Parámetros de un ensayo (valores por defecto: DECISIONES-PRUEBA.md).

    Attributes:
        n_agentes: tamaño de la colonia (C4).
        limite: máximo de ticks del ensayo, verificación incluida (I11).
        rho: evaporación por tick (I3).
        semilla: semilla de las agentes y del canal.
        agente, madre: configuración de las agentes y de la madre.
        radio, p_perdida, retardo, formato: parámetros del canal.
        registrar: si se guarda la posición de cada agente y la serie de métricas en cada tick.
        pausa: segundos que duerme cada hilo entre dos pasos (solo motor de hilos).
        salida_cada: ticks entre la salida de una agente y la siguiente (J1). Con 0 salen
            todas en el tick 0.
    """

    n_agentes: int = 6
    limite: int = 2000
    rho: float = 0.01
    semilla: int = 0
    agente: ConfigAgente = field(default_factory=ConfigAgente)
    madre: ConfigMadre = field(default_factory=ConfigMadre)
    radio: int = 1
    p_perdida: float = 0.0
    retardo: tuple[int, int] = (0, 0)
    formato: str = "binario"
    registrar: bool = False
    pausa: float = 0.0002
    salida_cada: int = 0


@dataclass
class Resultado:
    """Lo que deja un ensayo."""

    motivo: str  #: "verificada", "verificadora_fallo" o "limite"
    asentadas: bool  #: todas las agentes llegaron a la meta y se quedaron
    verificada: bool  #: además, la verificadora llegó siguiendo el rastro (criterio G1)
    ticks_asentadas: int | None  #: tick en que se asentó la última agente
    ticks_total: int
    largo_optimo: int  #: movimientos de la ruta óptima (BFS)
    largo_verificado: int | None  #: movimientos de la ruta de la verificadora
    bloqueadas: int  #: acciones que el mundo rechazó
    trafico: dict[str, dict[str, int]]  #: mensajes y bytes por familia
    memoria_madre: int  #: bytes que recuerda la madre al terminar
    modo_madre: str = "ausente"
    conocimiento: float | None = None  #: fracción del mundo que la madre conoce bien
    historial: list[tuple[int, int, Celda]] = field(default_factory=list)
    serie: list[dict[str, float]] = field(default_factory=list)  #: evolución tick a tick
    #: feromona de cada celda (por filas) al cerrar cada tick; solo con ``registrar``
    feromona: list[list[float]] = field(default_factory=list)
    ruta_verificada: list[Celda] | None = None  #: celdas de la ruta de la verificadora

    @property
    def razon(self) -> float | None:
        """Largo de la ruta verificada dividido por el óptimo (1.0 = ruta óptima)."""
        if self.largo_verificado is None:
            return None
        return self.largo_verificado / self.largo_optimo


class ActorMundo:
    """El lado del mundo: da a cada agente su percepción y ejecuta sus acciones."""

    def __init__(self, mundo: Mundo, canal: CanalMemoria, rho: float, registrar: bool) -> None:
        self.mundo = mundo
        self.canal = canal
        self.rho = rho
        self.registrar = registrar
        self.pos: dict[int, Celda] = {}
        self.ok: dict[int, bool] = {}
        self.activos: set[int] = set()  #: agentes que ya salieron del nido
        self.bloqueadas = 0
        self.historial: list[tuple[int, int, Celda]] = []
        canal.registrar(ID_MUNDO)

    def agregar(self, id_agente: int, activo: bool = True) -> None:
        """Pone un agente en el nido. Si no está activo, espera allí sin percibir ni actuar."""
        self.pos[id_agente] = self.mundo.inicio
        self.ok[id_agente] = True
        if activo:
            self.activos.add(id_agente)

    def enviar_percepciones(self, ahora: int) -> None:
        """Envía a cada agente activo lo que ve desde su celda."""
        for i in sorted(self.activos):
            otras = [c for j, c in self.pos.items() if j != i]
            self.canal.enviar(crear(
                "PERCEPCION", src=ID_MUNDO, dst=i, tick=ahora % 65536,
                pos=celda_a_byte(self.pos[i]), ok=int(self.ok[i]),
                vecinas=self.mundo.percibir(self.pos[i], otras)))

    def aplicar_acciones(self, ahora: int) -> set[int]:
        """Ejecuta las ACCION que hayan llegado. Devuelve los agentes atendidos."""
        atendidos = set()
        for msg in self.canal.recibir(ID_MUNDO):
            if nombre_de(msg) != "ACCION":  # las difusiones de la madre también le llegan
                continue
            i = msg["src"]
            self.pos[i], self.ok[i] = self.mundo.aplicar_accion(
                self.pos[i], msg["accion"], msg["dir"], msg["deposito"])
            self.bloqueadas += not self.ok[i]
            if self.registrar:
                self.historial.append((ahora, i, self.pos[i]))
            atendidos.add(i)
        return atendidos

    def cerrar_tick(self) -> None:
        """Fin del tick: la feromona se evapora."""
        self.mundo.evaporar(self.rho)


class Simulacion:
    """Arma un ensayo sobre un mundo y lo hace correr con uno de los dos motores."""

    def __init__(self, mundo: Mundo, config: ConfigEnsayo | None = None) -> None:
        self.mundo = mundo
        self.config = cfg = config or ConfigEnsayo()
        self.ctx = Contexto(mundo.ancho, mundo.alto, 8)
        self.actor_mundo: ActorMundo
        self.canal = CanalMemoria(
            self.ctx, posicion=lambda i: self.actor_mundo.pos.get(i), radio=cfg.radio,
            p_perdida=cfg.p_perdida, retardo=cfg.retardo, semilla=cfg.semilla, formato=cfg.formato)
        self.actor_mundo = ActorMundo(mundo, self.canal, cfg.rho, cfg.registrar)
        self.con_madre = cfg.madre.modo is not Modo.AUSENTE
        self.madre = Madre(self.canal, cfg.madre, self.ctx)
        self._config_agente = replace(
            cfg.agente, con_madre=self.con_madre, verificadora=False,
            informa_mapa=cfg.madre.modo in (Modo.RESCATE, Modo.DIFUSION))
        self.agentes = [Agente(i, self.canal, self._config_agente, cfg.semilla)
                        for i in range(1, cfg.n_agentes + 1)]
        for agente in self.agentes:
            self.actor_mundo.agregar(agente.id, activo=cfg.salida_cada == 0)
        self.verificadora: Agente | None = None
        self.ticks_asentadas: int | None = None
        self.serie: list[dict[str, float]] = []
        self.feromona: list[list[float]] = []
        self.tick = 0

    # ------------------------------------------------------------------ fases

    def _todas_asentadas(self) -> bool:
        return all(a.estado is Estado.ASENTADA for a in self.agentes)

    def _lanzar_verificadora(self) -> Agente:
        config = replace(self._config_agente, verificadora=True, informa_mapa=False)
        self.verificadora = Agente(self.config.n_agentes + 1, self.canal, config,
                                   self.config.semilla)
        self.actor_mundo.agregar(self.verificadora.id)
        return self.verificadora

    def _soltar(self) -> None:
        """Activa a las agentes cuyo turno de salir del nido ya llegó (J1)."""
        cada = self.config.salida_cada
        if cada:
            for j, agente in enumerate(self.agentes):
                if self.tick >= j * cada:
                    self.actor_mundo.activos.add(agente.id)

    def _avanzar_fase(self) -> tuple[bool, Agente | None]:
        """Revisa la fase al empezar un tick. Devuelve (terminó, verificadora recién lanzada)."""
        self._soltar()
        if self.verificadora is None:
            if self._todas_asentadas():
                self.ticks_asentadas = self.tick
                return False, self._lanzar_verificadora()
            return False, None
        return self.verificadora.estado in (Estado.ASENTADA, Estado.FALLIDA), None

    def _conocimiento(self) -> float | None:
        from ..metricas import conocimiento_del_mundo  # aquí para no crear un ciclo de imports

        return conocimiento_del_mundo(self.madre, self.mundo) if self.con_madre else None

    def _registrar_tick(self) -> None:
        """Guarda las métricas del tick que acaba de terminar (solo si ``registrar``)."""
        if not self.config.registrar:
            return
        trafico = self.canal.trafico
        self.serie.append({
            "tick": self.tick,
            "llegaron": sum(a.llegadas >= 1 for a in self.agentes),
            "asentadas": sum(a.estado is Estado.ASENTADA for a in self.agentes),
            "conocimiento": self._conocimiento(),
            "bytes_madre": trafico[2].bytes + trafico[3].bytes,
        })
        m = self.mundo
        self.feromona.append([round(m.feromona((x, y)), 6)
                              for y in range(m.alto) for x in range(m.ancho)])

    def _resultado(self) -> Resultado:
        v = self.verificadora
        verificada = v is not None and v.estado is Estado.ASENTADA
        if verificada:
            motivo = "verificada"
        elif v is not None and v.estado is Estado.FALLIDA:
            motivo = "verificadora_fallo"
        else:
            motivo = "limite"
        codigo = {"verificada": 0, "limite": 1, "verificadora_fallo": 2}[motivo]
        # Sin madre, el FIN es solo un aviso del motor: no cuenta como tráfico de la colonia.
        trafico = None if self.con_madre else self.canal.resumen()
        self.canal.enviar(crear("FIN", src=ID_MADRE, dst=ID_DIFUSION, tick=self.tick % 65536,
                                motivo=codigo))
        return Resultado(
            motivo=motivo,
            asentadas=self.ticks_asentadas is not None,
            verificada=verificada,
            ticks_asentadas=self.ticks_asentadas,
            ticks_total=self.tick,
            largo_optimo=self.mundo.largo_optimo(),
            largo_verificado=len(v.ruta) - 1 if verificada else None,
            bloqueadas=self.actor_mundo.bloqueadas,
            trafico=trafico or self.canal.resumen(),
            memoria_madre=self.madre.memoria_usada() if self.con_madre else 0,
            modo_madre=self.config.madre.modo.name.lower(),
            conocimiento=self._conocimiento(),
            historial=self.actor_mundo.historial,
            serie=self.serie,
            feromona=self.feromona,
            ruta_verificada=list(v.ruta) if verificada else None,
        )

    # ------------------------------------------------------------------ motores

    def correr(self, motor: str = "determinista") -> Resultado:
        """Corre el ensayo completo y devuelve su resultado."""
        if motor == "determinista":
            return self._correr_determinista()
        if motor == "hilos":
            return self._correr_hilos()
        raise ValueError("El motor es 'determinista' o 'hilos'")

    def _actores(self) -> list[Agente]:
        return self.agentes + ([self.verificadora] if self.verificadora else [])

    def _correr_determinista(self) -> Resultado:
        while self.tick < self.config.limite:
            termino, _ = self._avanzar_fase()
            if termino:
                break
            t = self.tick
            self.canal.avanzar(t)
            self.actor_mundo.enviar_percepciones(t)
            for agente in self._actores():
                agente.paso(t)
            self.actor_mundo.aplicar_acciones(t)
            self.madre.paso(t)
            self.actor_mundo.cerrar_tick()
            self._registrar_tick()
            self.tick += 1
        resultado = self._resultado()
        for agente in self._actores():  # entrega el FIN
            agente.paso(self.tick)
        return resultado

    def _correr_hilos(self) -> Resultado:
        parar = threading.Event()
        errores: list[BaseException] = []

        def bucle(actor) -> None:
            try:
                while not parar.is_set():
                    actor.paso(self.tick)
                    time.sleep(self.config.pausa)
            except BaseException as error:  # se vuelve a lanzar en el hilo principal
                errores.append(error)

        def arrancar(actor) -> threading.Thread:
            hilo = threading.Thread(target=bucle, args=(actor,), daemon=True)
            hilo.start()
            return hilo

        hilos = [arrancar(actor) for actor in (*self.agentes, self.madre)]
        try:
            while self.tick < self.config.limite:
                termino, nueva = self._avanzar_fase()
                if termino:
                    break
                if nueva is not None:
                    hilos.append(arrancar(nueva))
                t = self.tick
                self.canal.avanzar(t)
                self.actor_mundo.enviar_percepciones(t)
                pendientes = {a.id for a in self._actores()} & self.actor_mundo.activos
                plazo = time.monotonic() + 10
                while pendientes:  # pregunta-respuesta: espera la acción de cada agente
                    pendientes -= self.actor_mundo.aplicar_acciones(t)
                    if errores:
                        raise errores[0]
                    if time.monotonic() > plazo:
                        raise RuntimeError(f"Tick {t}: no respondieron los agentes {pendientes}")
                    if pendientes:
                        time.sleep(self.config.pausa)
                self.actor_mundo.cerrar_tick()
                self._registrar_tick()
                self.tick += 1
            resultado = self._resultado()
            time.sleep(20 * self.config.pausa)  # da tiempo a que lean el FIN
        finally:
            parar.set()
            for hilo in hilos:
                hilo.join(timeout=5)
        if errores:
            raise errores[0]
        return resultado
