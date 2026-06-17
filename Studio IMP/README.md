# Studio IMP

Prototipo inicial de editor online estilo Premiere, enfocado en la parte visual + funcional local.

## Funcionalidades actuales

- Importar multiples archivos de video/audio local sin reemplazar lo ya cargado
- Panel de medios del proyecto (media bin) para seleccionar clips rapidamente
- Timeline con pistas dinamicas: + Video y + Audio
- Eliminacion de pistas (audio/video) desde la propia timeline
- Regla de tiempo y barra de desplazamiento horizontal en timeline
- Arrastre de clips de izquierda a derecha para reubicar inicio en tiempo
- Controles por pista estilo NLE: VIS/LOCK para video y M/S/LOCK para audio
- Zoom de timeline y cabezal vertical (playhead) dentro de la linea de tiempo
- Seleccion de pista activa y clip activo para editar
- Reproduccion y control de playhead
- Recorte por tiempo de inicio/fin del clip activo
- Filtros cinematograficos + ajustes manuales (brillo/contraste/saturacion)
- Fundidos de video (visual) y audio (automatico)
- Pista de textos en timeline con clips movibles y duracion editable
- Cada texto nuevo se crea con duracion inicial de 5 segundos
- Copiar/Pegar textos (botones y atajos Ctrl/Cmd + C / Ctrl/Cmd + V)
- Capas de texto sobre el video con posicion arrastrable
- Keyframes de volumen por clip en pistas de audio
- Reproduccion de clips de audio en timeline durante play global
- Exportacion directa desde la interfaz (MP4 si el navegador lo soporta, fallback WebM)
- Historial de proyecto con Deshacer/Rehacer (botones y atajos Ctrl/Cmd+Z, Ctrl/Cmd+Y)

## Ejecutar

No requiere build ni backend.

1. Abrir index.html en un navegador moderno.
2. Crear pistas con + Video y + Audio si hace falta.
3. Importar uno o varios archivos con el boton Importar Media.
4. Arrastrar clips en timeline para ajustar su posicion horizontal.
5. Hacer clic en un clip para editarlo desde los paneles laterales.
6. Usar el boton Exportar MP4 para descargar el resultado.

## Alcance de esta fase

La fase actual permite exportacion basica con MediaRecorder y depende de codecs soportados por el navegador.
La siguiente etapa puede implementar serializacion de proyecto (JSON), re-apertura de sesiones y export MP4 por transcodificacion avanzada.
