"""Motor de ejecución del gemelo: planificador determinista y ejecución multihilo."""

from __future__ import annotations

import threading
from dataclasses import dataclass, replace
from enum import IntEnum
from typing import Any

from ..agente import Agente, ConfigAgente, Estado
from ..canal import CanalMemoria
from ..madre import ConfigMadre, Madre, Modo
from ..mundo.mundo import Celda, Mundo
from ..protocolo import (
    FLAG_ACK,
    ID_DIFUSION,
    ID_MADRE,
    ID_MUNDO,
    Contexto,
    celda_a_byte,
    crear,
    nombre_de,
)


class MotivoFin(IntEnum):
    VERIFICADA = 0
    LIMITE_PASOS = 1
    VERIFICADORA_FALLO = 2
    ABORTADO = 3


@dataclass
class ConfigMotor:
    n_agentes: int = 6
    max_ticks: int = 2000
    rho: float = 0.0
    config_agente: ConfigAgente | None = None
    config_madre: ConfigMadre | None = None
    radio: int = 1
    p_perdida: float = 0.0
    retardo: tuple[int, int] = (0, 0)
    formato_canal: str = "binario"
    verificar: bool = True
    registrar_historial: bool = True


@dataclass
class ResultadoEnsayo:
    semilla: int
    modo_madre: Modo
    convergio: bool
    motivo_fin: MotivoFin
    etapa_final: str
    ticks_totales: int
    ticks_exploracion: int | None
    ticks_verificacion: int | None
    agentes_asentadas: int
    largo_optimo: int | None
    largo_verificado: int | None
    razon_calidad: float | None
    ruta_verificada: list[Celda]
    rutas_exploradoras: dict[int, list[Celda]]
    historial: list[tuple[int, int, Celda]]
    feromona_final: dict[Celda, float]
    trafico: dict[str, dict[str, int]]
    bytes_madre_agentes: int
    bytes_totales: int
    memoria_madre_max: int
    rescatadas: list[int]
    bloqueadas: int

    def resumen_fila(self, etiqueta: str = "") -> dict[str, Any]:
        return {
            "etiqueta": etiqueta,
            "semilla": self.semilla,
            "modo_madre": self.modo_madre.name,
            "convergio": int(self.convergio),
            "motivo_fin": self.motivo_fin.name,
            "etapa_final": self.etapa_final,
            "ticks_totales": self.ticks_totales,
            "ticks_exploracion": self.ticks_exploracion,
            "ticks_verificacion": self.ticks_verificacion,
            "agentes_asentadas": self.agentes_asentadas,
            "largo_optimo": self.largo_optimo,
            "largo_verificado": self.largo_verificado,
            "razon_calidad": self.razon_calidad,
            "bytes_madre_agentes": self.bytes_madre_agentes,
            "bytes_totales": self.bytes_totales,
            "memoria_madre_max": self.memoria_madre_max,
            "rescatadas": len(self.rescatadas),
            "bloqueadas": self.bloqueadas,
        }


class _BaseMotor:
    def __init__(self, config: ConfigMotor | None = None) -> None:
        self.config = config or ConfigMotor()
        if self.config.n_agentes < 1:
            raise ValueError("Se requiere al menos 1 agente explorador")
        if self.config.max_ticks < 1:
            raise ValueError("max_ticks debe ser >= 1")

    def _preparar(self, mundo: Mundo, semilla: int):
        cfg = self.config
        ctx = Contexto(ancho=mundo.ancho, alto=mundo.alto, vecindad=8)
        pos: dict[int, Celda] = {}
        ok: dict[int, bool] = {}
        canal = CanalMemoria(
            ctx=ctx,
            posicion=pos.get,
            radio=cfg.radio,
            p_perdida=cfg.p_perdida,
            retardo=cfg.retardo,
            semilla=semilla,
            formato=cfg.formato_canal,
        )
        canal.registrar(ID_MUNDO)

        cfg_madre = replace(cfg.config_madre) if cfg.config_madre else ConfigMadre(modo=Modo.AUSENTE)
        con_madre = cfg_madre.modo is not Modo.AUSENTE
        madre = Madre(canal, cfg_madre, ctx=ctx)

        base_ag = replace(cfg.config_agente) if cfg.config_agente else ConfigAgente()
        if cfg.config_agente is None:
            base_ag.con_madre = con_madre
            base_ag.informa_mapa = cfg_madre.modo in (Modo.RESCATE, Modo.DIFUSION)
        base_ag.verificadora = False

        exploradoras: list[Agente] = []
        for i in range(1, cfg.n_agentes + 1):
            agente = Agente(i, canal, replace(base_ag), semilla)
            exploradoras.append(agente)
            pos[i] = mundo.inicio
            ok[i] = True

        if con_madre:
            canal.enviar(
                crear(
                    "INICIO",
                    src=ID_MADRE,
                    dst=ID_DIFUSION,
                    tick=0,
                    flags=FLAG_ACK,
                    ancho_m1=mundo.ancho - 1,
                    alto_m1=mundo.alto - 1,
                    nido=celda_a_byte(mundo.inicio),
                    vecindad=1,
                    modo_com=0,
                    modo_madre=int(cfg_madre.modo),
                    verificadora=0,
                    semilla=semilla & 0xFFFF,
                    delta_t=cfg_madre.delta_t,
                    K=base_ag.K,
                )
            )

        return ctx, pos, ok, canal, madre, cfg_madre, base_ag, exploradoras

    def _crear_verificadora(
        self, mundo: Mundo, semilla: int, canal: CanalMemoria, base_ag: ConfigAgente, pos, ok
    ) -> Agente:
        id_verif = self.config.n_agentes + 1
        cfg_verif = replace(base_ag, verificadora=True, informa_mapa=False)
        verificadora = Agente(id_verif, canal, cfg_verif, semilla)
        pos[id_verif] = mundo.inicio
        ok[id_verif] = True
        return verificadora

    @staticmethod
    def _enviar_percepciones(
        mundo: Mundo, canal: CanalMemoria, pos: dict[int, Celda], ok: dict[int, bool],
        activos: list[Agente], tick: int
    ) -> None:
        for agente in activos:
            otras = [c for i, c in pos.items() if i != agente.id]
            canal.enviar(
                crear(
                    "PERCEPCION",
                    src=ID_MUNDO,
                    dst=agente.id,
                    tick=tick % 65536,
                    pos=celda_a_byte(pos[agente.id]),
                    ok=int(ok[agente.id]),
                    vecinas=mundo.percibir(pos[agente.id], otras),
                )
            )

    def _procesar_acciones(
        self, mundo: Mundo, canal: CanalMemoria, pos: dict[int, Celda], ok: dict[int, bool],
        tick: int, historial: list[tuple[int, int, Celda]]
    ) -> int:
        bloqueadas = 0
        acciones = [m for m in canal.recibir(ID_MUNDO) if nombre_de(m) == "ACCION"]
        acciones.sort(key=lambda m: m["src"])
        for msg in acciones:
            i = msg["src"]
            pos[i], ok[i] = mundo.aplicar_accion(pos[i], msg["accion"], msg["dir"], msg["deposito"])
            if not ok[i]:
                bloqueadas += 1
            if self.config.registrar_historial:
                historial.append((tick, i, pos[i]))
        return bloqueadas

    def _vaciar_pendientes(
        self, canal: CanalMemoria, madre: Madre, tick_actual: int
    ) -> int:
        t = tick_actual
        max_espera = self.config.retardo[1] + 1
        for _ in range(max_espera):
            if canal.pendientes() == 0 or madre.verificacion is not None:
                break
            t += 1
            canal.avanzar(t)
            madre.paso(t)
        return t

    @staticmethod
    def _emitir_fin(
        canal: CanalMemoria, madre: Madre, todos: list[Agente], tick: int, motivo: MotivoFin
    ) -> None:
        canal.enviar(
            crear(
                "FIN",
                src=ID_MADRE,
                dst=ID_DIFUSION,
                tick=tick % 65536,
                flags=FLAG_ACK,
                motivo=int(motivo),
            )
        )
        for agente in todos:
            agente.paso(tick)
        madre.paso(tick)

    @staticmethod
    def _empaquetar(
        mundo: Mundo,
        semilla: int,
        cfg_madre: ConfigMadre,
        motivo_fin: MotivoFin,
        etapa_final: str,
        ticks_totales: int,
        ticks_exploracion: int | None,
        ticks_verificacion: int | None,
        exploradoras: list[Agente],
        verificadora: Agente | None,
        historial: list[tuple[int, int, Celda]],
        canal: CanalMemoria,
        madre: Madre,
        memoria_madre_max: int,
        bloqueadas: int,
    ) -> ResultadoEnsayo:
        convergio = motivo_fin is MotivoFin.VERIFICADA
        largo_optimo = mundo.largo_optimo()
        ruta_verif = list(verificadora.ruta) if (verificadora is not None and convergio) else []
        largo_verif = (len(ruta_verif) - 1) if (convergio and ruta_verif) else None
        razon = (
            (largo_verif / largo_optimo)
            if (largo_verif is not None and largo_optimo is not None and largo_optimo > 0)
            else None
        )
        trafico = canal.resumen()
        bytes_madre = trafico["agente_madre"]["bytes"] + trafico["madre_agente"]["bytes"]
        bytes_totales = sum(v["bytes"] for v in trafico.values())
        return ResultadoEnsayo(
            semilla=semilla,
            modo_madre=cfg_madre.modo,
            convergio=convergio,
            motivo_fin=motivo_fin,
            etapa_final=etapa_final,
            ticks_totales=ticks_totales,
            ticks_exploracion=ticks_exploracion,
            ticks_verificacion=ticks_verificacion,
            agentes_asentadas=sum(a.estado is Estado.ASENTADA for a in exploradoras),
            largo_optimo=largo_optimo,
            largo_verificado=largo_verif,
            razon_calidad=razon,
            ruta_verificada=ruta_verif,
            rutas_exploradoras={a.id: list(a.ruta) for a in exploradoras},
            historial=historial,
            feromona_final={c: mundo.feromona(c) for c in mundo.celdas_libres()},
            trafico=trafico,
            bytes_madre_agentes=bytes_madre,
            bytes_totales=bytes_totales,
            memoria_madre_max=memoria_madre_max,
            rescatadas=sorted(madre.rescatadas),
            bloqueadas=bloqueadas,
        )


class MotorDeterminista(_BaseMotor):
    """Ejecuta el ensayo de forma determinista y auditable con semilla."""

    def ejecutar(self, mundo: Mundo, semilla: int = 0) -> ResultadoEnsayo:
        _, pos, ok, canal, madre, cfg_madre, base_ag, exploradoras = self._preparar(mundo, semilla)
        historial: list[tuple[int, int, Celda]] = []
        bloqueadas = 0
        memoria_max = madre.memoria_usada()
        etapa = "exploracion"
        verificadora: Agente | None = None
        ticks_exploracion: int | None = None
        ticks_verificacion: int | None = None
        motivo_fin: MotivoFin | None = None
        etapa_final = "limite_exploracion"
        tick_final = 0

        for t in range(self.config.max_ticks):
            tick_final = t + 1
            canal.avanzar(t)
            activos = exploradoras if etapa == "exploracion" else [verificadora]
            self._enviar_percepciones(mundo, canal, pos, ok, activos, t)
            for agente in activos:
                agente.paso(t)
            bloqueadas += self._procesar_acciones(mundo, canal, pos, ok, t, historial)
            madre.paso(t)
            memoria_max = max(memoria_max, madre.memoria_usada())
            mundo.evaporar(self.config.rho)

            if etapa == "exploracion":
                if all(a.estado is Estado.ASENTADA for a in exploradoras):
                    ticks_exploracion = t + 1
                    if not self.config.verificar:
                        motivo_fin = MotivoFin.VERIFICADA
                        etapa_final = "exploracion_completada"
                        break
                    verificadora = self._crear_verificadora(mundo, semilla, canal, base_ag, pos, ok)
                    etapa = "verificacion"
                    etapa_final = "limite_verificacion"
                elif all(a.estado in (Estado.ASENTADA, Estado.FALLIDA) for a in exploradoras):
                    motivo_fin = MotivoFin.ABORTADO
                    etapa_final = "abortado"
                    break
            else:
                assert verificadora is not None
                if verificadora.estado in (Estado.ASENTADA, Estado.FALLIDA):
                    ticks_verificacion = (t + 1) - (ticks_exploracion or 0)
                    t_cierre = self._vaciar_pendientes(canal, madre, t)
                    memoria_max = max(memoria_max, madre.memoria_usada())
                    if verificadora.estado is Estado.ASENTADA:
                        motivo_fin = MotivoFin.VERIFICADA
                        etapa_final = "verificada"
                    else:
                        motivo_fin = MotivoFin.VERIFICADORA_FALLO
                        etapa_final = "verificadora_fallo"
                    tick_final = t_cierre + 1
                    break

        if motivo_fin is None:
            motivo_fin = MotivoFin.LIMITE_PASOS

        todos = exploradoras + ([verificadora] if verificadora is not None else [])
        self._emitir_fin(canal, madre, todos, tick_final, motivo_fin)

        return self._empaquetar(
            mundo=mundo,
            semilla=semilla,
            cfg_madre=cfg_madre,
            motivo_fin=motivo_fin,
            etapa_final=etapa_final,
            ticks_totales=tick_final,
            ticks_exploracion=ticks_exploracion,
            ticks_verificacion=ticks_verificacion,
            exploradoras=exploradoras,
            verificadora=verificadora,
            historial=historial,
            canal=canal,
            madre=madre,
            memoria_madre_max=memoria_max,
            bloqueadas=bloqueadas,
        )


class _GrupoHilos:
    """Administra un hilo del SO por agente ejecutando el mismo paso(ahora)."""

    def __init__(self, agentes: list[Agente]) -> None:
        self.agentes = agentes
        self._inicio = threading.Barrier(len(agentes) + 1)
        self._fin = threading.Barrier(len(agentes) + 1)
        self._tick = 0
        self._detener = False
        self._error: BaseException | None = None
        self._hilos = [
            threading.Thread(target=self._bucle, args=(agente,), daemon=True, name=f"agente-{agente.id}")
            for agente in agentes
        ]
        for hilo in self._hilos:
            hilo.start()

    def _bucle(self, agente: Agente) -> None:
        while True:
            self._inicio.wait()
            if self._detener:
                return
            try:
                agente.paso(self._tick)
            except BaseException as exc:  # pragma: no cover
                self._error = exc
            finally:
                self._fin.wait()

    def paso(self, tick: int) -> None:
        self._tick = tick
        self._inicio.wait()
        self._fin.wait()
        if self._error is not None:
            raise RuntimeError("Error en hilo de agente") from self._error

    def cerrar(self) -> None:
        self._detener = True
        self._inicio.wait()
        for hilo in self._hilos:
            hilo.join(timeout=2.0)


class MotorHilos(_BaseMotor):
    """Ejecuta el mismo Agente.paso(ahora) con un hilo concurrente por agente."""

    def ejecutar(self, mundo: Mundo, semilla: int = 0) -> ResultadoEnsayo:
        _, pos, ok, canal, madre, cfg_madre, base_ag, exploradoras = self._preparar(mundo, semilla)
        historial: list[tuple[int, int, Celda]] = []
        bloqueadas = 0
        memoria_max = madre.memoria_usada()
        etapa = "exploracion"
        verificadora: Agente | None = None
        ticks_exploracion: int | None = None
        ticks_verificacion: int | None = None
        motivo_fin: MotivoFin | None = None
        etapa_final = "limite_exploracion"
        tick_final = 0

        grupo = _GrupoHilos(exploradoras)
        try:
            for t in range(self.config.max_ticks):
                tick_final = t + 1
                canal.avanzar(t)
                activos = exploradoras if etapa == "exploracion" else [verificadora]
                self._enviar_percepciones(mundo, canal, pos, ok, activos, t)
                grupo.paso(t)
                bloqueadas += self._procesar_acciones(mundo, canal, pos, ok, t, historial)
                madre.paso(t)
                memoria_max = max(memoria_max, madre.memoria_usada())
                mundo.evaporar(self.config.rho)

                if etapa == "exploracion":
                    if all(a.estado is Estado.ASENTADA for a in exploradoras):
                        ticks_exploracion = t + 1
                        if not self.config.verificar:
                            motivo_fin = MotivoFin.VERIFICADA
                            etapa_final = "exploracion_completada"
                            break
                        grupo.cerrar()
                        verificadora = self._crear_verificadora(mundo, semilla, canal, base_ag, pos, ok)
                        grupo = _GrupoHilos([verificadora])
                        etapa = "verificacion"
                        etapa_final = "limite_verificacion"
                    elif all(a.estado in (Estado.ASENTADA, Estado.FALLIDA) for a in exploradoras):
                        motivo_fin = MotivoFin.ABORTADO
                        etapa_final = "abortado"
                        break
                else:
                    assert verificadora is not None
                    if verificadora.estado in (Estado.ASENTADA, Estado.FALLIDA):
                        ticks_verificacion = (t + 1) - (ticks_exploracion or 0)
                        t_cierre = self._vaciar_pendientes(canal, madre, t)
                        memoria_max = max(memoria_max, madre.memoria_usada())
                        if verificadora.estado is Estado.ASENTADA:
                            motivo_fin = MotivoFin.VERIFICADA
                            etapa_final = "verificada"
                        else:
                            motivo_fin = MotivoFin.VERIFICADORA_FALLO
                            etapa_final = "verificadora_fallo"
                        tick_final = t_cierre + 1
                        break
        finally:
            grupo.cerrar()

        if motivo_fin is None:
            motivo_fin = MotivoFin.LIMITE_PASOS

        todos = exploradoras + ([verificadora] if verificadora is not None else [])
        self._emitir_fin(canal, madre, todos, tick_final, motivo_fin)

        return self._empaquetar(
            mundo=mundo,
            semilla=semilla,
            cfg_madre=cfg_madre,
            motivo_fin=motivo_fin,
            etapa_final=etapa_final,
            ticks_totales=tick_final,
            ticks_exploracion=ticks_exploracion,
            ticks_verificacion=ticks_verificacion,
            exploradoras=exploradoras,
            verificadora=verificadora,
            historial=historial,
            canal=canal,
            madre=madre,
            memoria_madre_max=memoria_max,
            bloqueadas=bloqueadas,
        )


def simular(
    mundo: Mundo,
    semilla: int = 0,
    config: ConfigMotor | None = None,
    multihilo: bool = False,
) -> ResultadoEnsayo:
    motor = MotorHilos(config) if multihilo else MotorDeterminista(config)
    return motor.ejecutar(mundo, semilla=semilla)
