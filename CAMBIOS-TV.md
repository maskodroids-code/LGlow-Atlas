# LGlow para webOS

Esta carpeta reúne LGlow y las adaptaciones realizadas para dos televisores LG. Lee primero el README original y las guías de instalación y desinstalación.

| Modelo | Firmware | Aplicación de inicio |
|---|---|---|
| 43UN7300PSC | 04.64.00 | com.webos.app.fullhome |
| 50UP7500PSF | 03.53.45 | com.webos.app.home |

- **adaptaciones/** contiene los paquetes de trabajo por firmware, incluidos parches de inicio, clima e indicadores de Chile y salvapantallas.
- **herramientas-locales/** conserva los scripts y componentes usados para el marco, el selector de intervalo, la ubicación manual, la fecha y hora, el viento, la humedad, el índice UV y el comportamiento de Home. Estos scripts son referencias de despliegues sucesivos con precondiciones distintas. Antes de ejecutarlos, adapta las rutas y el destino SSH y revisa el orden de los parches. El instalador original no incorpora automáticamente estas adaptaciones.
- **../recursos-locales/** contiene 17 obras originales y 17 versiones con marco, además del marco y los íconos. La licencia del código se incluye en LICENSE. Verifica el permiso de redistribución de las imágenes e íconos antes de añadirlos a un repositorio público.

Los parches se aplican sobre los archivos del firmware correspondiente. Consulta docs/ para regenerarlos con los archivos de tu propio televisor. Configura TMDB con tu propia clave usando tv/config.example.json.

Este archivo se armó a partir de copias locales. La última versión instalada en cada televisor no pudo cotejarse por SSH.
