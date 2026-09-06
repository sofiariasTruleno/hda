# Orquestación de Trabajos — Hogar de los Alpes

Microservicio del bounded context **Gestión de Trabajos**, implementado con DDD táctico, arquitectura hexagonal y comunicación por eventos.

Grupo Capa Anticorrupción — Entrega 3, MISO.

---

## Cómo correrlo

```bash
pip install -r requirements.txt

make pruebas     # 23 pruebas
make demo        # ciclo de vida completo en consola
make servidor    # API en http://localhost:5000
```

Sin Make:

```bash
PYTHONPATH=src python -m pytest tests/ -v
PYTHONPATH=src python demo.py
PYTHONPATH=src python main.py
```

`demo.py` es lo más útil para la sustentación: imprime el ciclo completo mostrando en qué orden ocurren el commit, los eventos de dominio y los eventos de integración.

---

## Dónde está cada punto de la rúbrica

| Ítem (9 pts c/u) | Archivos |
|---|---|
| Patrón dominio: entidades, objetos valor, seedwork, servicios, módulos, agregaciones, fábricas, repositorios | `seedwork/dominio/`, `modulos/trabajos/dominio/` |
| Arquitectura hexagonal (puertos y adaptadores) | Puertos: `dominio/repositorios.py`. Adaptadores: `infraestructura/repositorios.py`, `api/trabajos.py` |
| Manejador de base de datos | `config/db.py`, `config/uow.py`, `trabajos/infraestructura/dto.py` |
| Comunicación entre módulos por eventos de dominio | `seedwork/aplicacion/handlers.py`, `modulos/cumplimiento/`, `modulos/seguimiento/` |
| Patrón CQS | `aplicacion/comandos/` vs `aplicacion/queries/` |

---

## Estructura

```
src/hda/
  seedwork/                      código base, sin conocimiento de HDA
    dominio/                     Entidad, AgregacionRaiz, ObjetoValor,
                                 EventoDominio, ReglaNegocio, puertos
    aplicacion/                  Comando, Query, despachador de dominio
    infraestructura/             UnidadTrabajo, despachador de integración

  modulos/
    trabajos/                    módulo core — la agregación Trabajo
      dominio/                   entidades, objetos valor, reglas, eventos,
                                 fábricas, puerto de repositorio
      aplicacion/                comandos, queries, DTOs, mapeadores
      infraestructura/           SQLAlchemy, repositorios, esquemas v1

    cumplimiento/                módulo interno — escucha SLAIncumplido
    seguimiento/                 módulo interno — proyección de lectura

  config/                        base de datos y unidad de trabajo
  api/                           adaptador HTTP (Flask)
```

Los tres módulos viven **dentro del mismo microservicio**. No son servicios separados. Se comunican solo por eventos de dominio.

---

## Modelo de dominio

Corresponde a la agregación Trabajo de la vista de información HDA-004.

**Raíz:** `Trabajo`
**Entidades internas:** `Diagnostico`, `Novedad`, `Ejecucion`
**Objetos valor:** `EstadoSolicitud`, `CategoriaDeServicio`, `Urgencia`, `Canal`, `Direccion`, `VentanaDeAtencion`, `DescripcionDelProblema`, `AcuerdoDeServicio`
**Referencias externas por identidad:** `DuenoDeHogarId`, `PartnerId`, `MercadoId`, `ProveedorId`, `CotizacionId`

### Ciclo de vida

```
REGISTRADO ──> ASIGNADO ──> EN_EJECUCION ──> COMPLETADO
     │             │              │
     └─────────────┴──────────────┴────────> CANCELADO
```

La máquina de estados vive en un solo lugar: `TransicionDeEstadoValida` en `dominio/reglas.py`.

---

## API

| Método | Ruta | Tipo |
|---|---|---|
| POST | `/trabajos` | comando |
| PUT | `/trabajos/{id}/proveedor` | comando |
| POST | `/trabajos/{id}/diagnostico` | comando |
| POST | `/trabajos/{id}/ejecucion` | comando |
| POST | `/trabajos/{id}/novedades` | comando |
| POST | `/trabajos/{id}/completar` | comando |
| GET | `/trabajos/{id}` | query |
| GET | `/trabajos?estado=&mercado_id=` | query |
| GET | `/trabajos/{id}/seguimiento` | query sobre proyección |

Ejemplo:

```bash
curl -X POST http://localhost:5000/trabajos -H "Content-Type: application/json" -d '{
  "dueno_de_hogar_id": "dh-001",
  "mercado_id": "CO",
  "categoria": "PLOMERIA",
  "urgencia": "ALTA",
  "canal": "MARKETPLACE",
  "descripcion": "Fuga de agua bajo el lavaplatos",
  "direccion": {"linea": "Calle 100 #15-20", "ciudad": "Bogota", "pais": "Colombia"},
  "ventana_atencion": {"inicio": "2026-09-08T09:00:00", "fin": "2026-09-08T13:00:00"}
}'
```

---

## Guía de defensa

Las preguntas que el tutor puede hacer y dónde está la respuesta en el código.

**¿Por qué `Diagnostico`, `Novedad` y `Ejecucion` son entidades internas y no agregaciones propias?**
Porque no tienen ciclo de vida transaccional autónomo fuera de la orden de servicio. Nadie consulta una Ejecución sin su Trabajo. Está en HDA-004 y en el docstring de `dominio/entidades.py`.

**¿Por qué `AgregacionRaiz` acumula eventos en vez de publicarlos de inmediato?**
Por transaccionalidad. Si se publicara dentro del método de negocio y luego el commit fallara, habría eventos anunciando hechos que nunca ocurrieron. La `UnidadTrabajo` publica solo después del commit. Ver `seedwork/infraestructura/uow.py`, y la prueba `test_eventos_solo_se_publican_tras_el_commit`.

**¿Cuál es la diferencia entre evento de dominio y evento de integración aquí?**
El de dominio se queda dentro del microservicio y comunica módulos: `SLAIncumplido` lo consume el módulo Cumplimiento. El de integración sale por el bus como published language, se versiona y es contrato: `TrabajoCompletadoIntegracion` lo consumen Confianza y Reputación, Pagos y Liquidación. Ver `trabajos/dominio/eventos.py`.

**¿Dónde está el puerto y dónde el adaptador?**
`dominio/repositorios.py` declara `RepositorioTrabajos` como interfaz abstracta. `infraestructura/repositorios.py` la implementa con SQLAlchemy. El dominio no importa nada de infraestructura. La evidencia es que `tests/test_dominio.py` corre sin base de datos y sin Flask.

**¿Por qué hay dos mapeadores?**
Son dos traducciones distintas. `aplicacion/mapeadores.py` traduce dominio ↔ DTO para la API. `infraestructura/mapeadores.py` traduce dominio ↔ tabla para la persistencia. Si fueran uno solo, un cambio en el esquema de la base afectaría el contrato HTTP.

**¿Por qué las entidades no heredan de `Base` de SQLAlchemy?**
Porque el ORM dictaría cómo se modela el negocio. Las tablas están en `infraestructura/dto.py`, separadas del dominio, y el mapeador traduce entre las dos.

**¿Qué separa CQS aquí en la práctica?**
Los comandos abren unidad de trabajo, mutan agregados y emiten eventos. Las queries no abren unidad de trabajo, no mutan y no emiten nada. Además hay dos repositorios: `RepositorioTrabajosSQLAlchemy` para escritura y `RepositorioTrabajosLectura`, que lanza excepción si se intenta escribir. Eso deja abierto apuntar las lecturas a una réplica sin tocar el modelo de escritura.

**¿Por qué una invariante violada devuelve 409 y no 500?**
Porque el sistema funciona correctamente; la operación es la que no procede. Un 500 diría que hubo una falla técnica. Ver los manejadores de error en `api/__init__.py`.

**¿Dónde se conecta esto con los escenarios de calidad?**
`mercado_id` es la clave de partición del bus y el filtro de las queries: es el aislamiento por mercado del escenario SC-ESC-02. La proyección de Seguimiento es el lado de lectura que permite escalar las consultas del SC-ESC-01. `TrabajoCompletadoIntegracion` es el disparador del recálculo masivo de reputación del SC-ESC-03.

**¿Por qué el agregado no emite eventos al rehidratarse desde la base?**
Porque reconstruir no es un hecho de negocio nuevo. `dto_a_entidad` llama a `limpiar_eventos()` explícitamente.

---

## Alcance y recortes conscientes

Lo que quedó fuera, deliberadamente:

- Cancelaciones con reglas de penalización y reprogramaciones
- Disputas y garantías post-servicio
- Adaptador real de Kafka: el puerto está definido y `DespachadorKafka` está esbozado, pero la entrega corre con `DespachadorEnMemoria` para no depender de un broker
- Autenticación y autorización: son capacidades genéricas tercerizadas según la vista de contexto

La consistencia entre agregaciones es eventual y se propaga por eventos. No hay transacciones distribuidas, coherente con la decisión de una base de datos por servicio.
