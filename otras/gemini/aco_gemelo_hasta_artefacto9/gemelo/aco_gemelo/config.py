"""Carga y validación de configuración YAML para el gemelo ACO (artefacto 9)."""

from __future__ import annotations

import copy
import random
import re
from dataclasses import dataclass, field, replace
from fractions import Fraction
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

from .agente import ConfigAgente
from .madre import ConfigMadre, Modo
from .motor import ConfigMotor
from .mundo.escenarios import mundo_aleatorio, mundo_l, puente_doble
from .mundo.mundo import Celda, Mundo

ESCENARIOS_VALIDOS = ("l", "aleatorio", "puente_doble", "personalizado")
DEPOSITOS_VALIDOS = ("calidad", "constante")
FORMATOS_VALIDOS = ("binario", "json")

_CLAVES_RAIZ = {"etiqueta", "mundo", "agente", "madre", "motor", "experimento"}
_CLAVES_MUNDO = {
    "escenario",
    "ancho",
    "alto",
    "densidad",
    "distancia_minima",
    "r",
    "obstaculos",
    "inicio",
    "meta",
    "tau0",
    "tau_max",
    "unidad_deposito",
}
_CLAVES_AGENTE = {
    "alpha",
    "k",
    "theta",
    "K",
    "deposito",
    "deposito_valor",
    "delta_t",
    "con_madre",
    "informa_mapa",
}
_CLAVES_MADRE = {
    "modo",
    "delta_t",
    "memoria",
    "umbral_rescate",
    "rutas_por_anuncio",
}
_CLAVES_MOTOR = {
    "n_agentes",
    "max_ticks",
    "rho",
    "radio",
    "p_perdida",
    "retardo",
    "formato_canal",
    "verificar",
    "registrar_historial",
    "multihilo",
}
_CLAVES_EXPERIMENTO = {
    "semilla",
    "semillas",
    "modos",
    "barrido",
    "salida_csv",
    "por_condicion",
}


def _numero_o_fraccion(valor: Any, nombre: str) -> float:
    if isinstance(valor, bool):
        raise ValueError(f"'{nombre}' debe ser numérico, no booleano")
    if isinstance(valor, (int, float)):
        return float(valor)
    if isinstance(valor, str):
        texto = valor.strip()
        try:
            return float(Fraction(texto))
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"'{nombre}' tiene un valor numérico inválido: {valor!r}") from exc
    raise ValueError(f"'{nombre}' debe ser numérico, no {type(valor).__name__}")


def _fraccion(valor: Any, nombre: str) -> int | Fraction:
    if isinstance(valor, bool):
        raise ValueError(f"'{nombre}' debe ser numérico, no booleano")
    if isinstance(valor, int):
        return valor
    if isinstance(valor, (float, str)):
        try:
            return Fraction(str(valor).strip())
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"'{nombre}' tiene un valor inválido: {valor!r}") from exc
    raise ValueError(f"'{nombre}' debe ser numérico, no {type(valor).__name__}")


def _entero(valor: Any, nombre: str, minimo: int | None = None) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError(f"'{nombre}' debe ser un entero, no {valor!r}")
    if minimo is not None and valor < minimo:
        raise ValueError(f"'{nombre}' debe ser >= {minimo}, recibido {valor}")
    return valor


def _booleano(valor: Any, nombre: str) -> bool:
    if not isinstance(valor, bool):
        raise ValueError(f"'{nombre}' debe ser booleano (true/false), no {valor!r}")
    return valor


def _celda(valor: Any, nombre: str) -> Celda:
    if (
        not isinstance(valor, (list, tuple))
        or len(valor) != 2
        or any(isinstance(c, bool) or not isinstance(c, int) for c in valor)
    ):
        raise ValueError(f"'{nombre}' debe ser una coordenada [x, y] de enteros, no {valor!r}")
    return (valor[0], valor[1])


def parsear_modo(valor: Any) -> Modo:
    """Convierte un nombre o código entero al enum Modo."""
    if isinstance(valor, Modo):
        return valor
    if isinstance(valor, int) and not isinstance(valor, bool):
        try:
            return Modo(valor)
        except ValueError as exc:
            raise ValueError(f"Código de modo desconocido: {valor}") from exc
    if isinstance(valor, str):
        clave = valor.strip().upper().replace("-", "_").replace(" ", "_")
        if clave in Modo.__members__:
            return Modo[clave]
    validos = ", ".join(Modo.__members__.keys())
    raise ValueError(f"Modo de madre inválido: {valor!r}. Opciones válidas: {validos}")


def resolver_semillas(spec: Any) -> list[int]:
    """Convierte la especificación de semillas del YAML o CLI en una lista ordenada de enteros."""
    if isinstance(spec, int) and not isinstance(spec, bool):
        if spec < 1:
            raise ValueError("La cantidad de semillas debe ser >= 1")
        return list(range(spec))
    if isinstance(spec, list):
        if not spec:
            raise ValueError("La lista de semillas no puede estar vacía")
        return [_entero(s, "semillas[]", minimo=0) for s in spec]
    if isinstance(spec, dict):
        claves = set(spec.keys())
        if not claves <= {"inicio", "cantidad", "fin", "paso"}:
            desconocidas = sorted(claves - {"inicio", "cantidad", "fin", "paso"})
            raise ValueError(f"Claves desconocidas en 'semillas': {desconocidas}")
        inicio = _entero(spec.get("inicio", 0), "semillas.inicio", minimo=0)
        paso = _entero(spec.get("paso", 1), "semillas.paso", minimo=1)
        if "cantidad" in spec:
            cantidad = _entero(spec["cantidad"], "semillas.cantidad", minimo=1)
            return [inicio + i * paso for i in range(cantidad)]
        if "fin" in spec:
            fin = _entero(spec["fin"], "semillas.fin", minimo=inicio + 1)
            return list(range(inicio, fin, paso))
        raise ValueError("El bloque 'semillas' requiere 'cantidad' o 'fin'")
    if isinstance(spec, str):
        texto = spec.strip()
        if ":" in texto:
            partes = texto.split(":")
            if len(partes) not in (2, 3):
                raise ValueError(f"Rango de semillas inválido: {spec!r}")
            nums = [int(p) for p in partes]
            if nums[1] <= nums[0]:
                raise ValueError(f"Rango de semillas vacío o decreciente: {spec!r}")
            return list(range(*nums))
        if "," in texto:
            semillas = [int(p.strip()) for p in texto.split(",") if p.strip()]
            if not semillas:
                raise ValueError(f"Lista de semillas inválida: {spec!r}")
            return semillas
        cantidad = int(texto)
        if cantidad < 1:
            raise ValueError("La cantidad de semillas debe ser >= 1")
        return list(range(cantidad))
    raise ValueError(f"Formato de semillas no soportado: {spec!r}")


def _validar_claves(datos: dict[str, Any], permitidas: set[str], seccion: str) -> None:
    desconocidas = sorted(set(datos.keys()) - permitidas)
    if desconocidas:
        raise ValueError(f"Claves desconocidas en '{seccion}': {desconocidas}")


@dataclass
class ConfigMundo:
    escenario: str = "l"
    ancho: int = 8
    alto: int = 8
    densidad: float = 0.2
    distancia_minima: int | None = 4
    r: int | Fraction = 2
    obstaculos: list[Celda] = field(default_factory=list)
    inicio: Celda | None = None
    meta: Celda | None = None
    tau0: float = 0.0
    tau_max: float = 1.0
    unidad_deposito: float = 1.0 / 255.0


@dataclass
class ConfigExperimento:
    semilla: int = 0
    semillas: list[int] = field(default_factory=lambda: list(range(30)))
    modos: list[Modo] | None = None
    barrido: dict[str, list[Any]] = field(default_factory=dict)
    salida_csv: str = "resultados/experimento.csv"
    por_condicion: bool = False


@dataclass
class ConfigEnsayo:
    etiqueta: str = "ensayo"
    mundo: ConfigMundo = field(default_factory=ConfigMundo)
    agente: ConfigAgente = field(default_factory=ConfigAgente)
    madre: ConfigMadre = field(default_factory=ConfigMadre)
    motor: ConfigMotor = field(default_factory=ConfigMotor)
    experimento: ConfigExperimento = field(default_factory=ConfigExperimento)
    multihilo: bool = False
    agente_con_madre_explicito: bool | None = None
    agente_informa_mapa_explicito: bool | None = None
    agente_delta_t_explicito: int | None = None
    datos_crudos: dict[str, Any] = field(default_factory=dict, repr=False)


def _cargar_yaml_basico(texto: str) -> Any:
    """Respaldo mínimo cuando PyYAML no está disponible en el entorno."""
    import json

    lineas: list[tuple[int, str]] = []
    for raw in texto.splitlines():
        sin_com = re.sub(r"(^|\s)#.*$", "", raw).rstrip()
        if not sin_com.strip():
            continue
        indent = len(sin_com) - len(sin_com.lstrip(" "))
        lineas.append((indent, sin_com.lstrip(" ")))

    def escalar(tok: str) -> Any:
        t = tok.strip()
        if t in ("null", "Null", "NULL", "~", ""):
            return None
        if t in ("true", "True", "TRUE"):
            return True
        if t in ("false", "False", "FALSE"):
            return False
        if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
            return t[1:-1]
        if t.startswith("[") and t.endswith("]"):
            return json.loads(t)
        if t.startswith("{") and t.endswith("}"):
            return json.loads(t)
        try:
            return int(t)
        except ValueError:
            pass
        try:
            return float(t)
        except ValueError:
            pass
        return t

    def parse_bloque(idx: int, indent_actual: int) -> tuple[Any, int]:
        if idx >= len(lineas):
            return {}, idx
        _, primero = lineas[idx]
        if primero.startswith("- "):
            lista: list[Any] = []
            while idx < len(lineas) and lineas[idx][0] == indent_actual and lineas[idx][1].startswith("- "):
                item_txt = lineas[idx][1][2:].strip()
                idx += 1
                if not item_txt:
                    sub, idx = parse_bloque(idx, indent_actual + 2)
                    lista.append(sub)
                elif ":" in item_txt and not item_txt.startswith(("[", "{", '"', "'")):
                    k, v = item_txt.split(":", 1)
                    d = {k.strip(): escalar(v)}
                    if idx < len(lineas) and lineas[idx][0] > indent_actual:
                        sub, idx = parse_bloque(idx, lineas[idx][0])
                        if isinstance(sub, dict):
                            d.update(sub)
                    lista.append(d)
                else:
                    lista.append(escalar(item_txt))
            return lista, idx

        mapa: dict[str, Any] = {}
        while idx < len(lineas) and lineas[idx][0] == indent_actual:
            _, contenido = lineas[idx]
            if ":" not in contenido:
                raise ValueError(f"Línea YAML inválida: {contenido!r}")
            clave, resto = contenido.split(":", 1)
            clave = clave.strip()
            resto = resto.strip()
            idx += 1
            if resto == "":
                if idx < len(lineas) and lineas[idx][0] > indent_actual:
                    sub, idx = parse_bloque(idx, lineas[idx][0])
                    mapa[clave] = sub
                else:
                    mapa[clave] = None
            else:
                mapa[clave] = escalar(resto)
        return mapa, idx

    if not lineas:
        return {}
    resultado, _ = parse_bloque(0, lineas[0][0])
    return resultado


def parsear_yaml(texto: str) -> dict[str, Any]:
    """Analiza texto YAML y devuelve el diccionario raíz validado."""
    if yaml is not None:
        datos = yaml.safe_load(texto)
    else:  # pragma: no cover
        datos = _cargar_yaml_basico(texto)
    if datos is None:
        return {}
    if not isinstance(datos, dict):
        raise ValueError("La raíz del archivo YAML debe ser un mapeo (clave: valor)")
    return datos


def cargar_config_desde_dict(datos: dict[str, Any]) -> ConfigEnsayo:
    """Construye y valida un ConfigEnsayo a partir de un diccionario."""
    if not isinstance(datos, dict):
        raise ValueError("La configuración debe ser un diccionario")
    _validar_claves(datos, _CLAVES_RAIZ, "raíz")

    etiqueta = str(datos.get("etiqueta", "ensayo"))

    # 1. Mundo
    sec_mundo = datos.get("mundo") or {}
    if not isinstance(sec_mundo, dict):
        raise ValueError("La sección 'mundo' debe ser un diccionario")
    _validar_claves(sec_mundo, _CLAVES_MUNDO, "mundo")

    escenario = str(sec_mundo.get("escenario", "l")).strip().lower()
    if escenario not in ESCENARIOS_VALIDOS:
        raise ValueError(
            f"Escenario desconocido: {escenario!r}. Opciones: {', '.join(ESCENARIOS_VALIDOS)}"
        )

    ancho_defecto = 3 if escenario == "puente_doble" else 8
    ancho = _entero(sec_mundo.get("ancho", ancho_defecto), "mundo.ancho", minimo=1)
    alto = _entero(sec_mundo.get("alto", 8), "mundo.alto", minimo=1)
    densidad = _numero_o_fraccion(sec_mundo.get("densidad", 0.2), "mundo.densidad")
    if not 0.0 <= densidad < 1.0:
        raise ValueError("mundo.densidad debe estar en [0, 1)")

    dist_raw = sec_mundo.get("distancia_minima", 4 if escenario in ("l", "aleatorio") else None)
    distancia_minima = None if dist_raw in (None, 0) else _entero(dist_raw, "mundo.distancia_minima", minimo=1)

    r_val = _fraccion(sec_mundo.get("r", 2), "mundo.r")
    if r_val < 1:
        raise ValueError("mundo.r debe ser >= 1")

    obstaculos_raw = sec_mundo.get("obstaculos", [])
    if not isinstance(obstaculos_raw, list):
        raise ValueError("mundo.obstaculos debe ser una lista de coordenadas [x, y]")
    obstaculos = [_celda(c, "mundo.obstaculos[]") for c in obstaculos_raw]

    inicio = _celda(sec_mundo["inicio"], "mundo.inicio") if sec_mundo.get("inicio") is not None else None
    meta = _celda(sec_mundo["meta"], "mundo.meta") if sec_mundo.get("meta") is not None else None

    tau0 = _numero_o_fraccion(sec_mundo.get("tau0", 0.0), "mundo.tau0")
    tau_max_def = 15.0 if escenario == "puente_doble" else 1.0
    tau_max = _numero_o_fraccion(sec_mundo.get("tau_max", tau_max_def), "mundo.tau_max")
    u_dep_def = 1.0 if escenario == "puente_doble" else (1.0 / 255.0)
    unidad_deposito = _numero_o_fraccion(
        sec_mundo.get("unidad_deposito", u_dep_def), "mundo.unidad_deposito"
    )
    if not 0.0 <= tau0 <= tau_max:
        raise ValueError("Se requiere 0 <= mundo.tau0 <= mundo.tau_max")

    cfg_mundo = ConfigMundo(
        escenario=escenario,
        ancho=ancho,
        alto=alto,
        densidad=densidad,
        distancia_minima=distancia_minima,
        r=r_val,
        obstaculos=obstaculos,
        inicio=inicio,
        meta=meta,
        tau0=tau0,
        tau_max=tau_max,
        unidad_deposito=unidad_deposito,
    )

    # 2. Madre
    sec_madre = datos.get("madre") or {}
    if not isinstance(sec_madre, dict):
        raise ValueError("La sección 'madre' debe ser un diccionario")
    _validar_claves(sec_madre, _CLAVES_MADRE, "madre")

    modo_madre = parsear_modo(sec_madre.get("modo", "PISTA_DE_BAILE"))
    delta_t_madre = _entero(sec_madre.get("delta_t", 10), "madre.delta_t", minimo=1)
    memoria_madre = _entero(sec_madre.get("memoria", 64), "madre.memoria", minimo=0)
    umbral_rescate = _numero_o_fraccion(sec_madre.get("umbral_rescate", 0.5), "madre.umbral_rescate")
    if umbral_rescate < 0:
        raise ValueError("madre.umbral_rescate debe ser >= 0")
    rutas_por_anuncio = _entero(
        sec_madre.get("rutas_por_anuncio", 3), "madre.rutas_por_anuncio", minimo=1
    )

    cfg_madre = ConfigMadre(
        modo=modo_madre,
        delta_t=delta_t_madre,
        memoria=memoria_madre,
        umbral_rescate=umbral_rescate,
        rutas_por_anuncio=rutas_por_anuncio,
    )

    # 3. Agente
    sec_agente = datos.get("agente") or {}
    if not isinstance(sec_agente, dict):
        raise ValueError("La sección 'agente' debe ser un diccionario")
    _validar_claves(sec_agente, _CLAVES_AGENTE, "agente")

    alpha = _numero_o_fraccion(sec_agente.get("alpha", 2.0), "agente.alpha")
    k_def = 20.0 if escenario == "puente_doble" else 1.0
    k_val = _numero_o_fraccion(sec_agente.get("k", k_def), "agente.k")
    theta = _numero_o_fraccion(sec_agente.get("theta", 8.0), "agente.theta")
    K_mem = _entero(sec_agente.get("K", 64), "agente.K", minimo=1)
    dep_def = "constante" if escenario == "puente_doble" else "calidad"
    deposito = str(sec_agente.get("deposito", dep_def)).strip().lower()
    if deposito not in DEPOSITOS_VALIDOS:
        raise ValueError(f"agente.deposito debe ser uno de {DEPOSITOS_VALIDOS}, no {deposito!r}")
    deposito_valor = _entero(sec_agente.get("deposito_valor", 1), "agente.deposito_valor", minimo=0)

    delta_t_ag_raw = sec_agente.get("delta_t", None)
    delta_t_ag = (
        None if delta_t_ag_raw is None else _entero(delta_t_ag_raw, "agente.delta_t", minimo=1)
    )
    con_madre_raw = sec_agente.get("con_madre", None)
    con_madre_exp = (
        None if con_madre_raw is None else _booleano(con_madre_raw, "agente.con_madre")
    )
    informa_mapa_raw = sec_agente.get("informa_mapa", None)
    informa_mapa_exp = (
        None if informa_mapa_raw is None else _booleano(informa_mapa_raw, "agente.informa_mapa")
    )

    con_madre_ef = (modo_madre is not Modo.AUSENTE) if con_madre_exp is None else con_madre_exp
    informa_mapa_ef = (
        (modo_madre in (Modo.RESCATE, Modo.DIFUSION))
        if informa_mapa_exp is None
        else informa_mapa_exp
    )

    cfg_agente = ConfigAgente(
        alpha=alpha,
        k=k_val,
        theta=theta,
        K=K_mem,
        deposito=deposito,
        deposito_valor=deposito_valor,
        delta_t=delta_t_madre if delta_t_ag is None else delta_t_ag,
        con_madre=con_madre_ef,
        verificadora=False,
        informa_mapa=informa_mapa_ef,
    )

    # 4. Motor
    sec_motor = datos.get("motor") or {}
    if not isinstance(sec_motor, dict):
        raise ValueError("La sección 'motor' debe ser un diccionario")
    _validar_claves(sec_motor, _CLAVES_MOTOR, "motor")

    n_agentes = _entero(sec_motor.get("n_agentes", 6), "motor.n_agentes", minimo=1)
    max_ticks = _entero(sec_motor.get("max_ticks", 2000), "motor.max_ticks", minimo=1)
    rho = _numero_o_fraccion(sec_motor.get("rho", 0.0), "motor.rho")
    if not 0.0 <= rho <= 1.0:
        raise ValueError("motor.rho debe estar entre 0 y 1")
    radio = _entero(sec_motor.get("radio", 1), "motor.radio", minimo=0)
    p_perdida = _numero_o_fraccion(sec_motor.get("p_perdida", 0.0), "motor.p_perdida")
    if not 0.0 <= p_perdida <= 1.0:
        raise ValueError("motor.p_perdida debe estar entre 0 y 1")

    retardo_raw = sec_motor.get("retardo", [0, 0])
    if (
        not isinstance(retardo_raw, (list, tuple))
        or len(retardo_raw) != 2
        or any(isinstance(x, bool) or not isinstance(x, int) for x in retardo_raw)
    ):
        raise ValueError("motor.retardo debe ser una pareja [min, max] de enteros")
    if not 0 <= retardo_raw[0] <= retardo_raw[1]:
        raise ValueError("Se requiere 0 <= motor.retardo[0] <= motor.retardo[1]")
    retardo = (retardo_raw[0], retardo_raw[1])

    formato_canal = str(sec_motor.get("formato_canal", "binario")).strip().lower()
    if formato_canal not in FORMATOS_VALIDOS:
        raise ValueError(f"motor.formato_canal debe ser uno de {FORMATOS_VALIDOS}")
    verificar = _booleano(sec_motor.get("verificar", True), "motor.verificar")
    registrar_historial = _booleano(
        sec_motor.get("registrar_historial", True), "motor.registrar_historial"
    )
    multihilo = _booleano(sec_motor.get("multihilo", False), "motor.multihilo")

    cfg_motor = ConfigMotor(
        n_agentes=n_agentes,
        max_ticks=max_ticks,
        rho=rho,
        config_agente=cfg_agente,
        config_madre=cfg_madre,
        radio=radio,
        p_perdida=p_perdida,
        retardo=retardo,
        formato_canal=formato_canal,
        verificar=verificar,
        registrar_historial=registrar_historial,
    )

    # 5. Experimento
    sec_exp = datos.get("experimento") or {}
    if not isinstance(sec_exp, dict):
        raise ValueError("La sección 'experimento' debe ser un diccionario")
    _validar_claves(sec_exp, _CLAVES_EXPERIMENTO, "experimento")

    semilla = _entero(sec_exp.get("semilla", 0), "experimento.semilla", minimo=0)
    semillas = resolver_semillas(sec_exp.get("semillas", {"inicio": 0, "cantidad": 30}))

    modos_raw = sec_exp.get("modos", None)
    modos = None if modos_raw is None else [parsear_modo(m) for m in modos_raw]
    if modos is not None and not modos:
        raise ValueError("experimento.modos no puede ser una lista vacía")

    barrido_raw = sec_exp.get("barrido", None)
    if barrido_raw is None:
        barrido: dict[str, list[Any]] = {}
    else:
        if not isinstance(barrido_raw, dict):
            raise ValueError("experimento.barrido debe ser un diccionario {ruta.param: [valores]}")
        barrido = {}
        for clave, valores in barrido_raw.items():
            if not isinstance(valores, list) or not valores:
                raise ValueError(f"experimento.barrido['{clave}'] debe ser una lista no vacía")
            barrido[str(clave)] = list(valores)

    salida_csv = str(sec_exp.get("salida_csv", "resultados/experimento.csv"))
    por_condicion = _booleano(sec_exp.get("por_condicion", False), "experimento.por_condicion")

    cfg_exp = ConfigExperimento(
        semilla=semilla,
        semillas=semillas,
        modos=modos,
        barrido=barrido,
        salida_csv=salida_csv,
        por_condicion=por_condicion,
    )

    cfg = ConfigEnsayo(
        etiqueta=etiqueta,
        mundo=cfg_mundo,
        agente=cfg_agente,
        madre=cfg_madre,
        motor=cfg_motor,
        experimento=cfg_exp,
        multihilo=multihilo,
        agente_con_madre_explicito=con_madre_exp,
        agente_informa_mapa_explicito=informa_mapa_exp,
        agente_delta_t_explicito=delta_t_ag,
        datos_crudos=copy.deepcopy(datos),
    )

    # Validar que las rutas de barrido sean válidas desde la carga
    for ruta_param, valores in barrido.items():
        for v in valores:
            aplicar_override(cfg, ruta_param, v)

    return cfg


def cargar_config(ruta: str | Path) -> ConfigEnsayo:
    """Carga y valida un archivo de configuración YAML desde disco."""
    path = Path(ruta)
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {path}")
    texto = path.read_text(encoding="utf-8")
    datos = parsear_yaml(texto)
    return cargar_config_desde_dict(datos)


def aplicar_override(cfg: ConfigEnsayo, ruta_param: str, valor: Any) -> ConfigEnsayo:
    """Devuelve una copia de ConfigEnsayo modificando un parámetro con notación 'seccion.clave'."""
    datos = copy.deepcopy(cfg.datos_crudos)
    partes = ruta_param.split(".")
    if len(partes) == 1:
        datos[partes[0]] = valor
    elif len(partes) == 2:
        sec, clave = partes
        datos.setdefault(sec, {})
        if not isinstance(datos[sec], dict):
            raise ValueError(f"La sección '{sec}' no admite subclave '{clave}'")
        datos[sec][clave] = valor
    else:
        raise ValueError(f"Ruta de parámetro no soportada: {ruta_param!r}")
    return cargar_config_desde_dict(datos)


def construir_mundo(cfg: ConfigEnsayo, semilla: int) -> Mundo:
    """Instancia el Mundo correspondiente al escenario configurado y la semilla."""
    m = cfg.mundo
    kwargs = dict(tau0=m.tau0, tau_max=m.tau_max, unidad_deposito=m.unidad_deposito)

    if m.escenario == "puente_doble":
        return puente_doble(r=m.r, ancho=m.ancho, **kwargs).mundo

    if m.escenario == "personalizado":
        if m.inicio is None or m.meta is None:
            raise ValueError("El escenario 'personalizado' requiere 'mundo.inicio' y 'mundo.meta'")
        mundo = Mundo(m.ancho, m.alto, m.obstaculos, m.inicio, m.meta, **kwargs)
        if mundo.bfs() is None:
            raise ValueError("En el escenario 'personalizado' la meta no es alcanzable desde el inicio")
        return mundo

    rng = random.Random(semilla)
    for _ in range(1000):
        if m.escenario == "l":
            mundo = mundo_l(rng, **kwargs)
        else:
            mundo = mundo_aleatorio(rng, ancho=m.ancho, alto=m.alto, densidad=m.densidad, **kwargs)
        if m.inicio is not None or m.meta is not None:
            ini = m.inicio if m.inicio is not None else mundo.inicio
            fin = m.meta if m.meta is not None else mundo.meta
            mundo = Mundo(mundo.ancho, mundo.alto, mundo.obstaculos, ini, fin, **kwargs)
            if mundo.bfs() is None:
                continue
        if m.distancia_minima is None:
            return mundo
        optimo = mundo.largo_optimo()
        if optimo is not None and optimo >= m.distancia_minima:
            return mundo
    raise RuntimeError(
        f"No se pudo generar un mundo '{m.escenario}' con distancia_minima >= {m.distancia_minima}"
    )


def construir_config_motor(cfg: ConfigEnsayo, modo_override: Modo | None = None) -> ConfigMotor:
    """Construye ConfigMotor listo para ejecutar, respetando el modo activo."""
    modo = cfg.madre.modo if modo_override is None else modo_override
    cfg_madre = replace(cfg.madre, modo=modo)

    con_madre = (
        (modo is not Modo.AUSENTE)
        if cfg.agente_con_madre_explicito is None
        else cfg.agente_con_madre_explicito
    )
    informa_mapa = (
        (modo in (Modo.RESCATE, Modo.DIFUSION))
        if cfg.agente_informa_mapa_explicito is None
        else cfg.agente_informa_mapa_explicito
    )
    delta_t_ag = (
        cfg_madre.delta_t
        if cfg.agente_delta_t_explicito is None
        else cfg.agente_delta_t_explicito
    )
    cfg_agente = replace(
        cfg.agente,
        con_madre=con_madre,
        informa_mapa=informa_mapa,
        delta_t=delta_t_ag,
        verificadora=False,
    )
    return replace(cfg.motor, config_agente=cfg_agente, config_madre=cfg_madre)
