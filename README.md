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



## Alcance y recortes conscientes

Lo que quedó fuera, deliberadamente:

- Cancelaciones con reglas de penalización y reprogramaciones
- Disputas y garantías post-servicio
- Adaptador real de Kafka: el puerto está definido y `DespachadorKafka` está esbozado, pero la entrega corre con `DespachadorEnMemoria` para no depender de un broker
- Autenticación y autorización: son capacidades genéricas tercerizadas según la vista de contexto

La consistencia entre agregaciones es eventual y se propaga por eventos. No hay transacciones distribuidas, coherente con la decisión de una base de datos por servicio.
