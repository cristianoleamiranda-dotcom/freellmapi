# Investigación aplicada de motion design

Documento de trabajo para la historia de 15 s de Abyss Tattoo Studio. No es teoría
suelta: cada punto termina en una decisión concreta del montaje.

## 1. Qué se está viendo en 2026

| Señal | Fuente | Qué implica para este proyecto |
|---|---|---|
| La tipografía cinética dejó de ser adorno: los reels controlan la velocidad de lectura partiendo la frase en unidades | [Advids, 15 motion design trends](https://advids.co/blog/motion-design-video) | Titular en dos tiempos («ESTO NO ES» / «UN TATUAJE»), no párrafos |
| Conviven dos escuelas de transición: cámara continua con whip-pan (57 % de los casos medidos) y cortes duros al golpe (43 %) | [Advids](https://advids.co/blog/motion-design-video) | Mezcla: cortes duros al pulso + punch zoom dentro del plano |
| El formato vertical se diseña nativo: texto más grande, encuadres más cerrados y ritmo más rápido | [Pixflow](https://pixflow.net/blog/top-video-editing-trends-2025/), [Motion Lab](https://motion-lab.agency/en/blog/tendances-motion-design-2026) | Texto +30–40 % respecto a un corte horizontal; nada por debajo de 40 px |
| Textura y grano vuelven como reacción al render plástico | [Critica TV](https://www.criticatv.com/motion-graphics-trends-how-visual-storytelling-is-evolving-in-2026/) | Grano fino + viñeta, sin look HDR |
| El minimalismo orgánico gana al exceso de capas | [Motion Lab](https://motion-lab.agency/en/blog/tendances-motion-design-2026) | Una capa de texto por plano, máximo dos |

## 2. Los cuatro actos, escalados a 15 s

La skill `motion-design` propone anticipación → acción → reacción → resolución, con
porcentajes que dependen de la duración total. En 15 s el reparto útil es:

| Acto | % | Tiempo | Función en el reel |
|---|---:|---|---|
| Anticipación / hook | 12 % | 0.0–1.8 s | Frenar el pulgar: macro + frase que rompe la expectativa |
| Acción | 48 % | 1.8–9.0 s | Portafolio, piercing y estudio al pulso |
| Reacción | 16 % | 9.0–11.4 s | Mosaico rítmico, clímax de montaje |
| Resolución | 24 % | 11.4–15.0 s | Emblema, CTA y dirección |

## 3. Rejilla musical

100 BPM = **0.6 s por negra**. Los 15 s son 25 negras exactas. Todos los cortes caen en
la rejilla:

```
0.0   1.8   3.6   5.4   7.2   8.4   9.6   11.4        15.0
|--P1--|--P2--|--P3--|--P4--|--P5--|--P6--|----P7----|---P8----|
 3b    3b    3b    3b    2b    2b      3b        6b
```

Ningún corte «a ojo»: si un plano no cabe en la rejilla, se cambia el plano, no el pulso.

## 4. Personalidad de movimiento

La skill define cuatro arquetipos. Para tatuaje el que corresponde es **Premium**
(350–600 ms, curva `cubic-bezier(0.4, 0, 0.2, 1)`, 0 % de overshoot): el tatuaje es
permanente y el rebote lo abarata. Eso fija tres constantes:

1. **Easing firma**: `easeOutCubic` para todo lo que aparece.
2. **Paleta de duraciones**: 320 ms (micro), 480 ms (título), 900 ms (revelado).
3. **Entrada**: desde abajo, 24 px, sin rotación.

Excepción medida: los **cortes** usan aceleración (`easeInCubic`) porque salir debe ser
más rápido que entrar. La propia skill lo pide: entrada decelerada, salida acelerada.

Materiales: piedra/metal = duración ×1.2 y 0 % de overshoot; fluido = ×1.5. El grano y
la viñeta se mueven como material rígido, no como gelatina.

## 5. Reglas de composición que se aplican

- **Regla del tercio (movimiento)**: ningún desplazamiento de cámara recorre más de 1/3
  del encuadre sin un keyframe. Por eso los zooms van de 1.00 a 1.18–1.22, no a 1.6.
- **Regla del tercio (elementos)**: como máximo un tercio de los elementos en movimiento
  a la vez. Si el título entra, la cámara se queda quieta.
- **Tres capas**: primaria (título o zoom), secundaria (hairline que aparece después del
  título) y ambiente (grano y respiración del encuadre).
- **Contraste sobre imagen**: como el material es oscuro y con textura, el texto va en
  Hueso `#B5A295` / Crema `#EAE3DD` con sombra suave, nunca en blanco puro.

## 6. Tipografía

- **Display**: Cinzel 700/800 (la del emblema). Mayúsculas, tracking +2 %. Para titulares.
- **Metadatos**: Montserrat 500/600, 32–40 px, tracking +8 %. Para dirección, WhatsApp y
  categorías.
- Jerarquía en dos niveles como máximo por plano: una línea display y una línea de
  metadatos. Nada de tres tamaños compitiendo.

## 7. Zonas seguras

Del sistema de la marca y de las guías de plataforma:

- Caja de texto: `x ∈ [84, 960]`, `y ∈ [210, 1500]`.
- Cabecera de Reels: no usar `y < 190`.
- Riel derecho (me gusta, comentarios, compartir): no usar `x > 960`.
- Descripción y barra de audio: no usar `y > 1500`.
- El CTA final puede bajar a `y ≈ 1700` solo cuando el resto del encuadre está limpio.

## 8. Qué se descarta y por qué

- **Transiciones de plantilla** (zoom blur genérico, glitch RGB, desplazamientos con
  rebote): leen a publicidad barata y contradicen el arquetipo Premium.
- **Texto con contorno o degradado**: resta legibilidad en pantalla pequeña.
- **Más de dos frases por plano**: el espectador no alcanza a leer antes del corte.
- **Música con drop agresivo**: el estudio vende precisión, no fiesta.
- **Datos no verificados** (años de experiencia, número de artistas, certificaciones):
  el montaje no afirma nada que no esté en las fuentes del propio estudio.

## 9. Cómo se traduce a la línea de tiempo

| Plano | Recurso | Cámara | Texto | Capa ambiente |
|---|---|---|---|---|
| P1 | macro aguja (hero_film f≈95) | push-in 1.00→1.16 | «ESTO NO ES» / «UN TATUAJE» | grano + viñeta |
| P2 | lobo rugido (foto) | pull-back 1.18→1.04 | «ES UNA FIRMA» | grano |
| P3 | manga cristo (foto) | pan vertical + zoom 1.10 | «PIEZA ÚNICA» | grano |
| P4 | ink wipe (proceso_detalle f≈190) | push-in 1.00→1.10 | «TRAZO A TRAZO» | grano |
| P5 | helix titanio (foto) | crash zoom 1.22→1.06 | «TITANIO» / «GRADO IMPLANTE» | grano |
| P6 | fachada / vitrina | dolly-in 1.00→1.12 | «SAN BERNARDO» / dirección | grano |
| P7 | mosaico 4 piezas | cortes internos al pulso | «BLACK & GREY» / «ORIENTAL» / «FULL COLOR» | grano |
| P8 | emblema Abyss | settle 1.06→1.00 | «AGENDA TU HORA» + CTA | halo teal |

Cada fila de esta tabla es un bloque de `src/timeline.py`; si cambia el guion, cambia la
tabla y se vuelve a renderizar.
