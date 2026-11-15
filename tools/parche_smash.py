#!/usr/bin/env python3
"""Parche de build para Smash Bros. Ultimate (aplicado al clon de nxnative
antes de compilar):

1. Traduce al español los textos del lanzador DmIOS (settings.tsv sin tocar
   la columna de sección, Launcher.swift con los títulos traducidos al
   mostrarlos, front_ios.m) y fija los ajustes de rendimiento por defecto
   del usuario: DM_OPMODE -> 0 (Portátil) y DM_PRESENT_SNAP -> 1 (buffer de
   fotogramas activado).
2. Controles táctiles rediseñados SOLO para Smash (DM_GAME_ID
   01006A800016E000), dentro de dm/ios/Sources/DmGamepad.m, según la vista
   previa v5 aprobada por el usuario el 2026-11-15 (set COMPLETO de Smash,
   estilo cristal oscuro, en los layouts 2D y 3D):
   - Stick izquierdo fijo abajo-izquierda; cruceta de burlas encima de él.
   - Diamante a la derecha: A (la mayor, en verde) = ataque, B = especial,
     X / Y = salto.
   - Hombros como pastillas arriba en las esquinas: ZL / ZR fuera,
     L / R debajo; L / R = escudo, ZL / ZR = agarrar (como en Switch).
   - Stick derecho (C) con anillo fijo abajo-derecha, para los smash con el
     stick; deja de ser un stick flotante sin dibujo.
   - + / - y la tuerca de ajustes de DmIOS quedan de fábrica, arriba en el
     centro.
   - L3 / R3 se ocultan: Smash no los usa para nada (no son asignables en
     el juego); serían dos círculos vacíos.
   Los índices B_* no se tocan: su orden es el de los bits DM_BTN_* del host.

Falla con error si alguna cadena esperada no aparece, para detectar cambios
de upstream. Uso: python3 parche_smash.py <ruta-al-clon-de-nxnative>
"""
import sys
from pathlib import Path

root = Path(sys.argv[1])
missing = []


def patch(relpath, pairs):
    p = root / relpath
    text = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in text:
            missing.append(f"{relpath}: no encontrado: {old!r}")
        else:
            text = text.replace(old, new)
    p.write_text(text, encoding="utf-8")


def patch_default(relpath, var, old_default, new_default):
    """Cambia la columna 'default' de la fila que empieza por <var> en un TSV."""
    p = root / relpath
    lines = p.read_text(encoding="utf-8").split("\n")
    done = False
    for i, line in enumerate(lines):
        if line.startswith(var + "\t"):
            cols = line.split("\t")
            for j, c in enumerate(cols):
                if c == old_default:
                    cols[j] = new_default
                    done = True
            lines[i] = "\t".join(cols)
    if not done:
        missing.append(f"{relpath}: default de {var}: no se encontró {old_default!r}")
    p.write_text("\n".join(lines), encoding="utf-8")


TSV = "dm/games/settings.tsv"

patch(TSV, [
    ("1=Docked,0=Handheld", "1=Televisor,0=Portátil"),
    ("0=Window,1=Fullscreen", "0=Ventana,1=Pantalla completa"),
    ("fit=Fit,fill=Fill", "fit=Ajustar,fill=Rellenar"),
    ("off=Standard,metalfx=MetalFX", "off=Estándar,metalfx=MetalFX"),
    ("game=Game's own,metalfx=MetalFX", "game=El del juego,metalfx=MetalFX"),
    ("auto=Match screen", "auto=Según la pantalla"),
    ("iPhone Duo screen (1.43:1)", "pantalla iPhone Duo (1,43:1)"),
    ("Frame rate", "Velocidad de fotogramas"),
    ("Dynamic resolution", "Resolución dinámica"),
    ("Render scale", "Escala de render"),
    ("Console mode", "Modo de consola"),
    ("Upscaling", "Reescalado"),
    ("Game's upscaler", "Reescalado del juego"),
    ("Game language", "Idioma del juego"),
    ("Display mode", "Modo de pantalla"),
    ("Picture shape", "Forma de la imagen"),
    ("\tPicture\t", "\tImagen\t"),
    ("Frame-rate counter", "Contador de FPS"),
    ("Touch feedback", "Vibración táctil"),
    ("Game rumble", "Vibración del juego"),
    ("Rumble strength", "Intensidad de la vibración"),
    ("Rumble cutoff", "Corte de vibración"),
    ("Press a button to join", "Pulsa un botón para unirte"),
    ("Switch 2 controllers", "Mandos de Switch 2"),
    ("Frame buffering", "Buffer de fotogramas"),
    ("Metal 4 pipelines", "Pipelines Metal 4"),
    ("Pipeline prebuild", "Precompilación de pipelines"),
    ("Encode thread", "Hilo de codificación"),
    ("Hold frames when late", "Retener fotogramas si hay retraso"),
    ("Performance HUD", "HUD de rendimiento"),
    ("Lets the game lower its resolution under load. Turn off to keep full resolution for the selected console mode.",
     "Permite que el juego baje su resolución cuando va cargado. Desactívalo para mantener la resolución completa del modo de consola elegido."),
    ("Uses more GPU time and can increase heat.",
     "Usa más tiempo de GPU y puede aumentar el calor."),
    ("Fill crops the game's 16:9 picture to cover the screen. Health bars, subtitles or maps near the edges can be cut off. A full-screen picture without cropping needs a patch for each game.",
     "Rellenar recorta la imagen 16:9 del juego para cubrir la pantalla. Las barras de vida, los subtítulos o los mapas cerca de los bordes pueden cortarse. Una imagen a pantalla completa sin recorte necesita un parche para cada juego."),
    ("Plays Joy-Con 2 and Pro Controller 2 over Bluetooth: hold Sync on one during the game to pair it. macOS asks once for Bluetooth access.",
     "Juega con Joy-Con 2 y Pro Controller 2 por Bluetooth: mantén Sync en uno durante el juego para enlazarlo. macOS pide el acceso Bluetooth una vez."),
    ("Renders about a quarter more pixels: a little slower and warmer.",
     "Renderiza una cuarta parte más de píxeles: un poco más lento y más caliente."),
    ("Up to one frame more display latency.",
     "Hasta un fotograma más de latencia de pantalla."),
    ("Keeps a pipeline archive; uses more memory.",
     "Mantiene un archivo de pipelines; usa más memoria."),
    ("The first start waits a few minutes for it, once.",
     "El primer inicio espera unos minutos por ello, una sola vez."),
])

patch_default(TSV, "DM_OPMODE", "DM_GAME_OPMODE", "0")
patch_default(TSV, "DM_PRESENT_SNAP", "DM_GAME_PRESENT_SNAP", "1")

patch("dm/ios/Sources/Launcher.swift", [
    ("Section(section) {",
     'Section(["Game": "Juego", "Controls": "Controles", "Performance": "Rendimiento"][section] ?? section) {'),
    ('"Play"', '"Jugar"'),
    ("Reset to tested defaults", "Restablecer los valores probados"),
    ("Brings back all settings this game was tested with.",
     "Recupera todos los ajustes con los que se probó este juego."),
    ("Memory available", "Memoria disponible"),
    ("Cloud saves", "Guardados en la nube"),
    ("Checking the cloud save", "Comprobando el guardado en la nube"),
    ("Choose a different folder", "Elige otra carpeta"),
    ("Choose a folder in iCloud Drive", "Elige una carpeta en iCloud Drive"),
    ("Saved. The game uses this folder when you press Play.",
     "Guardado. El juego usa esta carpeta cuando pulsas Jugar."),
    ("That folder could not be remembered", "No se pudo recordar esa carpeta"),
    ("try a different one.", "prueba con otra."),
    ("Turn off cloud saves", "Desactivar los guardados en la nube"),
    ("Play This iPhone's Save", "Jugar con la partida de este iPhone"),
    ("Play Without It", "Jugar sin ella"),
    ("Try Again", "Intentar de nuevo"),
    ('"Cancel"', '"Cancelar"'),
    ('"Version \\(', '"Versión \\('),
])

patch("dm/ios/Sources/front_ios.m", [
    ("Game files unusable.", "Los archivos del juego no se pueden usar."),
    ('"Game files"', '"Archivos del juego"'),
    ("Tap to start", "Toca para empezar"),
    ("Open the app again to start", "Abre la app otra vez para empezar"),
    ("The game restarts.", "El juego se reinicia."),
    ("Open the app again to continue.", "Abre la app otra vez para continuar."),
    ("Starting %@", "Iniciando %@"),
    ("This device is not supported.", "Este dispositivo no es compatible."),
    ('"Save failed"', '"Error al guardar"'),
    ("Saving failed (errno %d); progress was not saved.",
     "Error al guardar (errno %d); el progreso no se guardó."),
    ('"Cancel"', '"Cancelar"'),
])

# ---------------------------------------------------------------------------
# Controles rediseñados para Smash (un solo fichero: DmGamepad.m)
# ---------------------------------------------------------------------------

GATE = r'''
// ---- Controles tactiles redisenados, solo Smash (build privada del usuario) ----
// Set completo de Smash segun la vista previa aprobada (v5, 2026-11-15),
// estilo cristal oscuro, en los layouts 2D y 3D: stick izquierdo fijo,
// cruceta de burlas, diamante A/B/X/Y con la A mayor y en verde, hombros
// como pastillas (ZL/L y ZR/R), stick derecho con anillo fijo (deja de ser
// flotante y sin dibujo) y L3/R3 ocultos (Smash no los usa: no son
// asignables en el juego). + / - y la tuerca de ajustes quedan de fabrica.
// Los indices B_* no se tocan: su orden es el de los bits DM_BTN_* del host.
// Todo vive tras este gate; el resto de juegos queda igual.
#ifndef DM_GAME_ID
#define DM_GAME_ID ""
#endif
static BOOL smashPad(void) { return !strcmp(DM_GAME_ID, "01006A800016E000"); }
'''

HELPERS = r'''- (BOOL)smashActive { return smashPad() && !_tap && !_layout.separated; }
- (CGPoint)smashRStickCenter { CGRect c = _layout.controls; return CGPointMake(CGRectGetMinX(c) + 0.762 * c.size.width, CGRectGetMinY(c) + 0.845 * c.size.height); }
- (CGRect)smashRectFor:(int)b { CGRect c = _layout.controls; CGFloat x = CGRectGetMinX(c), y = CGRectGetMinY(c), w = c.size.width, h = c.size.height;
    switch (b) { case B_ZL: return CGRectMake(x + 0.042 * w, y + 0.044 * h, 0.066 * w, 0.062 * h);
        case B_L: return CGRectMake(x + 0.054 * w, y + 0.148 * h, 0.056 * w, 0.055 * h);
        case B_ZR: return CGRectMake(x + 0.892 * w, y + 0.044 * h, 0.066 * w, 0.062 * h);
        default: return CGRectMake(x + 0.890 * w, y + 0.148 * h, 0.056 * w, 0.055 * h); } }   // B_R
'''

LAYOUT_BLOCK = r'''    if ([self smashActive]) {
        static const int sh[4] = {B_ZL, B_L, B_ZR, B_R};
        for (int i = 0; i < 4; i++) { int b = sh[i]; CGRect rc = [self smashRectFor:b]; setPath(_key[b], CGPathCreateWithRoundedRect(rc, rc.size.height / 2, rc.size.height / 2, NULL)); placeLabel(_label[b], CGPointMake(CGRectGetMidX(rc), CGRectGetMidY(rc)), 15 * u); }
        setPath(_key[B_A], circlePath([self facePos:B_A], self.faceR * 1.18));
        setPath(_ring2, circlePath([self smashRStickCenter], [self stickR:1]));
        CGFloat k2 = [self stickR:1] * 0.5; _knob2.bounds = CGRectMake(0, 0, 2 * k2, 2 * k2); setPath(_knob2, circlePath(CGPointMake(k2, k2), k2));
        CAShapeLayer *kin2 = (CAShapeLayer *)_knob2.sublayers.firstObject; CGPathRef kip2 = circlePath(CGPointMake(k2, k2), k2 * 0.62); kin2.frame = _knob2.bounds; kin2.path = kip2; CGPathRelease(kip2);
    }
'''

GP = "dm/ios/Sources/DmGamepad.m"

patch(GP, [
    # colores nuevos: cristal oscuro de reposo y verde de la A
    ("static UIColor *k_idle, *k_on, *k_line, *k_ringFill, *k_text, *k_textOn;",
     "static UIColor *k_idle, *k_on, *k_line, *k_ringFill, *k_text, *k_textOn, *k_smashFill, *k_smashA, *k_smashAOn;"),
    ("k_ringFill = [UIColor colorWithWhite:1 alpha:0.06];",
     "k_ringFill = [UIColor colorWithWhite:1 alpha:0.06]; k_smashFill = [UIColor colorWithWhite:0 alpha:0.35]; k_smashA = [UIColor colorWithRed:0.13 green:0.50 blue:0.22 alpha:0.55]; k_smashAOn = [UIColor colorWithRed:0.16 green:0.65 blue:0.27 alpha:0.85];"),
    # gate, tras la lista de teclas bloqueadas
    ("static const int k_btns[] = {B_ZL, B_L, B_ZR, B_R, B_MINUS, B_PLUS, B_LS, B_RS};   // keys locked at touch-down (L3 / R3 only in the 3D layout)",
     "static const int k_btns[] = {B_ZL, B_L, B_ZR, B_R, B_MINUS, B_PLUS, B_LS, B_RS};   // keys locked at touch-down (L3 / R3 only in the 3D layout)" + GATE),
    # capas del stick derecho dibujado
    ("    CAShapeLayer *_key[B_N]; CATextLayer *_label[B_N];   // one layer per key",
     "    CAShapeLayer *_key[B_N]; CATextLayer *_label[B_N];   // one layer per key\n    CAShapeLayer *_ring2, *_knob2;   // stick derecho dibujado (solo en el modo Smash)"),
    ("""        _ring = shape(_controls); _ring.fillColor = k_ringFill.CGColor;
        _knob = shape(_controls);
        CAShapeLayer *in = [CAShapeLayer layer]; in.fillColor = nil; in.strokeColor = k_line.CGColor; in.lineWidth = 1.5;   // inner ring of the knob
        [_knob addSublayer:in];""",
     """        _ring = shape(_controls); _ring.fillColor = k_ringFill.CGColor;
        _knob = shape(_controls);
        CAShapeLayer *in = [CAShapeLayer layer]; in.fillColor = nil; in.strokeColor = k_line.CGColor; in.lineWidth = 1.5;   // inner ring of the knob
        [_knob addSublayer:in];
        _ring2 = shape(_controls); _ring2.fillColor = k_ringFill.CGColor; _ring2.hidden = YES;
        _knob2 = shape(_controls); _knob2.hidden = YES;
        CAShapeLayer *in2 = [CAShapeLayer layer]; in2.fillColor = nil; in2.strokeColor = k_line.CGColor; in2.lineWidth = 1.5;   // inner ring of the right knob
        [_knob2 addSublayer:in2];"""),
    # visibilidad: en Smash se ve todo en 2D y 3D, menos L3/R3 (sin uso en el juego)
    ("""    for (int b = 0; b < B_N; b++) _key[b].hidden = _tap || (fullOnly(b) && !_full);
    _ring.hidden = _knob.hidden = _tap;""",
     """    BOOL sm = [self smashActive];
    for (int b = 0; b < B_N; b++) _key[b].hidden = _tap || (sm ? (b == B_LS || b == B_RS) : (fullOnly(b) && !_full));
    _ring.hidden = _knob.hidden = _tap;
    _ring2.hidden = _knob2.hidden = _tap || !sm;"""),
    # geometria del diamante: centro y medidas de la vista previa
    ("- (CGPoint)faceCenter { CGRect s = self.corner; CGFloat u = self.u;",
     "- (CGPoint)faceCenter { if ([self smashActive]) { CGRect c = _layout.controls; return CGPointMake(CGRectGetMinX(c) + 0.862 * c.size.width, CGRectGetMinY(c) + 0.520 * c.size.height); } CGRect s = self.corner; CGFloat u = self.u;"),
    ("- (CGFloat)faceGap { return K_FACE_GAP * self.u; }",
     "- (CGFloat)faceGap { return [self smashActive] ? 0.066 * _layout.controls.size.width : K_FACE_GAP * self.u; }"),
    ("- (CGFloat)faceR { return K_FACE_R * self.u; }",
     "- (CGFloat)faceR { return [self smashActive] ? 0.028 * _layout.controls.size.width : K_FACE_R * self.u; }"),
    # radio de acierto sin solapes entre vecinos del diamante
    ("- (CGFloat)faceHitR { return MAX(self.faceR * 1.25, _layout.separated ? 22 : 0); }",
     "- (CGFloat)faceHitR { return [self smashActive] ? self.faceR * 1.15 : MAX(self.faceR * 1.25, _layout.separated ? 22 : 0); }"),
    # stick izquierdo en su sitio de la vista previa
    ("- (CGPoint)stickHome {\n    if (self.portraitControls) {",
     "- (CGPoint)stickHome {\n    if ([self smashActive]) { CGRect c = _layout.controls; return CGPointMake(CGRectGetMinX(c) + 0.105 * c.size.width, CGRectGetMinY(c) + 0.640 * c.size.height); }\n    if (self.portraitControls) {"),
    ("- (CGFloat)stickR:(int)i { return (i ? K_RSTICK_R : K_STICK_R) * self.u; }",
     "- (CGFloat)stickR:(int)i { if ([self smashActive]) return (i ? 0.034 : 0.058) * _layout.controls.size.width; return (i ? K_RSTICK_R : K_STICK_R) * self.u; }"),
    # cruceta en su sitio de la vista previa
    ("- (CGPoint)dpadCenter {\n    if (self.portraitControls) {",
     "- (CGPoint)dpadCenter {\n    if ([self smashActive]) { CGRect c = _layout.controls; return CGPointMake(CGRectGetMinX(c) + 0.105 * c.size.width, CGRectGetMinY(c) + 0.265 * c.size.height); }\n    if (self.portraitControls) {"),
    ("- (CGFloat)dpadR { return K_DPAD_R * self.u; }",
     "- (CGFloat)dpadR { return [self smashActive] ? 0.034 * _layout.controls.size.width : K_DPAD_R * self.u; }"),
    # metodos auxiliares, antes de menuDistance (la tuerquita NO se toca)
    ("- (CGFloat)menuDistance:(CGPoint)p {",
     HELPERS + "- (CGFloat)menuDistance:(CGPoint)p {"),
    # hit de los hombros por su rectangulo de pastilla
    ("""- (CGFloat)buttonDistance:(int)b point:(CGPoint)p {
    CGFloat u = self.u;""",
     """- (CGFloat)buttonDistance:(int)b point:(CGPoint)p {
    CGFloat u = self.u;
    if ([self smashActive] && isDrop(b)) { CGRect r = CGRectInset([self smashRectFor:b], -8 * u, -8 * u);
        if (!CGRectContainsPoint(r, p)) return CGFLOAT_MAX;
        return MAX(fabs(p.x - CGRectGetMidX(r)) / (r.size.width / 2), fabs(p.y - CGRectGetMidY(r)) / (r.size.height / 2)); }"""),
    # L3/R3 tampoco se pueden pulsar en Smash (están ocultos)
    ("        if (fullOnly(b) && !_full) continue;",
     "        if ((fullOnly(b) && !_full) || ([self smashActive] && isClick(b))) continue;"),
    # controlAt: la cruceta y el stick derecho fijo también reclaman el toque en 2D
    ("    if (_full && dist(p, self.dpadCenter) / MAX(self.dpadR * K_DPAD_GRAB, _layout.separated ? 22 : 0) < 1) return YES;",
     "    if ((_full || [self smashActive]) && dist(p, self.dpadCenter) / MAX(self.dpadR * K_DPAD_GRAB, _layout.separated ? 22 : 0) < 1) return YES;"),
    ("    return _full && !_stick[1] && [self inRightArea:p];",
     "    if ([self smashActive]) return !_stick[1] && dist(p, [self smashRStickCenter]) / MAX([self stickR:1] * K_STICK_GRAB, _layout.separated ? 22 : 0) < 1;\n    return _full && !_stick[1] && [self inRightArea:p];"),
    # touchesBegan: la cruceta reclama también en 2D si es Smash
    ("        if (_full) { CGFloat d = dist(p, self.dpadCenter) / MAX(self.dpadR * K_DPAD_GRAB, _layout.separated ? 22 : 0); if (d < best) { best = d; kind = C_DPAD; } }",
     "        if (_full || [self smashActive]) { CGFloat d = dist(p, self.dpadCenter) / MAX(self.dpadR * K_DPAD_GRAB, _layout.separated ? 22 : 0); if (d < best) { best = d; kind = C_DPAD; } }"),
    # touchesBegan: el stick derecho se reclama desde su anillo fijo; el flotante queda para el resto
    ("        if (kind == C_NONE && _full && !_stick[1] && [self inRightArea:p]) { kind = C_STICK; idx = 1; _rCentre = p; }   // the right stick: centred where the touch lands",
     "        if (kind == C_NONE && [self smashActive] && !_stick[1]) { CGFloat s = dist(p, [self smashRStickCenter]) / MAX([self stickR:1] * K_STICK_GRAB, _layout.separated ? 22 : 0); if (s <= 1) { kind = C_STICK; idx = 1; _rCentre = [self smashRStickCenter]; } }\n        if (kind == C_NONE && _full && !_stick[1] && ![self smashActive] && [self inRightArea:p]) { kind = C_STICK; idx = 1; _rCentre = p; }   // the right stick: centred where the touch lands"),
    # touchesMoved: en Smash el centro del stick derecho no sigue al dedo (es fijo)
    ("            if ((v >> 8) == 1) { CGFloat d = dist(p, _rCentre), R = [self stickR:1];   // the right stick's centre follows a finger past its radius, so turning back responds at once",
     "            if ((v >> 8) == 1 && ![self smashActive]) { CGFloat d = dist(p, _rCentre), R = [self stickR:1];   // the right stick's centre follows a finger past its radius, so turning back responds at once"),
    # recompute: refrescar también mientras se usa el stick derecho (su knob se mueve)
    ("    BOOL stick = _stick[0] != nil;   // only the left stick is drawn: the right one needs no refresh",
     "    BOOL stick = _stick[0] != nil || ([self smashActive] && _stick[1] != nil);   // only the left stick is drawn: the right one needs no refresh (en Smash si: tiene anillo propio)"),
    # dibujo Smash al final de layoutSubviews
    ("    [CATransaction commit];\n    [self refresh];\n}",
     LAYOUT_BLOCK + "    [CATransaction commit];\n    [self refresh];\n}"),
    # rellenos: cristal oscuro en reposo, la A en verde
    ("        _key[b].fillColor = (on ? k_on : k_idle).CGColor; _label[b].foregroundColor = (on ? k_textOn : k_text).CGColor; }",
     "        _key[b].fillColor = ([self smashActive] ? (on ? (b == B_A ? k_smashAOn : k_on) : (b == B_A ? k_smashA : k_smashFill)) : (on ? k_on : k_idle)).CGColor; _label[b].foregroundColor = (on ? k_textOn : k_text).CGColor; }"),
    # el knob del stick derecho sigue a su dedo y vuelve al centro
    ("    CGPoint h = self.stickHome, o = [self knobOffset:0];",
     "    if (_ring2) { BOOL sm = [self smashActive]; _ring2.hidden = _tap || !sm; _knob2.hidden = _tap || !sm; if (sm) { CGPoint rc = [self smashRStickCenter], ro = [self knobOffset:1]; _knob2.position = CGPointMake(rc.x + ro.x, rc.y + ro.y); _knob2.fillColor = (_stick[1] ? k_on : k_smashFill).CGColor; } }\n    CGPoint h = self.stickHome, o = [self knobOffset:0];"),
])

if missing:
    print("FALTAN PATRONES (¿cambió upstream?):")
    for m in missing:
        print(" -", m)
    sys.exit(1)

SECCIONES_OK = {"Game", "Controls", "Performance"}
for n, line in enumerate((root / TSV).read_text(encoding="utf-8").split("\n"), 1):
    if not line or line.startswith("#"):
        continue
    cols = line.split("\t")
    if len(cols) >= 6 and cols[5] not in SECCIONES_OK:
        print(f"ERROR ESTRUCTURAL: {TSV}:{n}: sección no válida: {cols[5]!r}")
        sys.exit(1)
print("Parche aplicado: lanzador en español + controles rediseñados para Smash.")
