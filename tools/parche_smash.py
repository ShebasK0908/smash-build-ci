#!/usr/bin/env python3
"""Parche de build para la app separada «Smash controles mobiles» (aplicado
al clon de nxnative antes de compilar):

1. Traduce al español los textos del lanzador DmIOS (settings.tsv sin tocar
   la columna de sección, Launcher.swift con los títulos traducidos al
   mostrarlos, front_ios.m) y fija los ajustes de rendimiento por defecto
   del usuario: DM_OPMODE -> 0 (Portátil) y DM_PRESENT_SNAP -> 1 (buffer de
   fotogramas activado).
2. Controles táctiles con el diseño bronce del usuario (su imagen de
   medallones, aprobada en la vista previa v9 el 2026-11-15), SOLO para
   Smash (DM_GAME_ID 01006A800016E000), dentro de dm/ios/Sources/
   DmGamepad.m. Los botones son los recortes de su propia imagen, incrustados
   como capas de arte (sprites en tools/sprites/*.b64):
   - Stick izquierdo con la moneda de base y el pomo que se mueve; cruceta
     de burlas a su derecha, con el arte de la cruz.
   - Stick derecho FIJO arriba a la derecha (anillo + pomo), para los smash.
   - A (verde, con resplandor) = ataque, B (grande) = especial, X / Y =
     saltar, cada uno en su sitio y tamaño de la imagen, no en diamante.
   - Pastillas arriba: L / ZL a la izquierda, ZR / R a la derecha
     (L / R = escudo, ZL / ZR = agarrar, como en Switch).
   - Zonas extra (mismo bit, segunda zona, como el R doble de Silksong):
     S = especial (B), escudo = L, puño = ataque (A), mano = agarrar (ZL) y
     la pestaña ZR de abajo = ZR.
   - + / - como medallones en su sitio; la tuerca de ajustes de DmIOS queda
     DE FÁBRICA entre ellos. L3 / R3 ocultos: Smash no los usa.
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
# Controles bronce para Smash (un solo fichero: DmGamepad.m)
# Los sprites salen de la imagen del usuario (tools/sprites/*.b64).
# ---------------------------------------------------------------------------

SPRITES_DIR = Path(__file__).resolve().parent / "sprites"


def b64_literal(name):
    data = (SPRITES_DIR / f"{name}.b64").read_text(encoding="ascii").strip()
    chunks = [data[i:i + 8192] for i in range(0, len(data), 8192)]
    return " ".join(f'@"{c}"' for c in chunks)


def img_fn(fn_name, cases, default="nil"):
    lines = [f"static UIImage *{fn_name}(int n) {{ switch (n) {{"]
    for key, sprite in cases:
        lines.append(f"        case {key}: return smashImg({b64_literal(sprite)});")
    lines.append(f"        default: return {default}; }} }}")
    return "\n".join(lines)


GATE = r'''
// ---- Controles bronce, solo Smash (build privada del usuario) ----
// Diseno del usuario (vista previa v9 aprobada el 2026-11-15): los botones
// son los medallones recortados de su propia imagen, incrustados como capas
// de arte sobre las teclas. A = ataque, B = especial, X / Y = saltar, cada
// uno en su sitio (no en diamante); pastillas L / ZL y ZR / R arriba (la ZR
// de arriba corrige el «ZL» duplicado de su imagen); stick derecho fijo
// arriba a la derecha; cruceta de burlas con su cruz; zonas extra con el
// mismo bit (S = B, escudo = L, puno = A, mano = ZL, pestana = ZR); la
// tuerca de ajustes de DmIOS queda de fabrica. L3 / R3 ocultos (Smash no
// los usa). Los indices B_* no se tocan: su orden es el de DM_BTN_*.
// Todo vive tras este gate; el resto de juegos queda igual.
#ifndef DM_GAME_ID
#define DM_GAME_ID ""
#endif
static BOOL smashPad(void) { return !strcmp(DM_GAME_ID, "01006A800016E000"); }
static const int k_zoneBit[5] = {B_B, B_L, B_A, B_ZL, B_ZR};   // zonas extra: S, escudo, puno, mano, pestana ZR
static CGRect smashFit(CGRect box, CGFloat aspect) { CGFloat h = box.size.width / aspect; return CGRectMake(box.origin.x, CGRectGetMidY(box) - h / 2, box.size.width, h); }
static UIImage *smashImg(NSString *b64) { NSData *d = [[NSData alloc] initWithBase64EncodedString:b64 options:0]; return d ? [UIImage imageWithData:d] : nil; }
'''

GATE += img_fn("smashArtFor", [
    ("B_A", "A"), ("B_B", "B"), ("B_X", "X"), ("B_Y", "Y"),
    ("B_L", "L"), ("B_R", "R"), ("B_ZL", "ZL"), ("B_ZR", "ZR"),
    ("B_PLUS", "plus"), ("B_MINUS", "minus"),
]) + "\n"
GATE += img_fn("smashZoneArtFor", [
    (0, "S"), (1, "shield"), (2, "fist"), (3, "hand"), (4, "ZRtab"),
]) + "\n"
GATE += img_fn("smashArtNamed", [
    (0, "dpad"), (1, "lstick"), (2, "rstick"),
]) + "\n"

HELPERS = r'''- (BOOL)smashActive { return smashPad() && !_tap && !_layout.separated; }
- (CGPoint)smashFaceCenter:(int)b { CGRect c = _layout.controls; CGFloat x = CGRectGetMinX(c), y = CGRectGetMinY(c), w = c.size.width, h = c.size.height;
    switch (b) { case B_A: return CGPointMake(x + 0.9185 * w, y + 0.801 * h);
        case B_B: return CGPointMake(x + 0.796 * w, y + 0.6545 * h);
        case B_X: return CGPointMake(x + 0.918 * w, y + 0.5635 * h);
        default: return CGPointMake(x + 0.8335 * w, y + 0.4635 * h); } }   // B_Y
- (CGFloat)smashFaceR:(int)b { CGFloat w = _layout.controls.size.width;
    switch (b) { case B_A: return 0.0615 * w; case B_B: return 0.062 * w; case B_X: return 0.049 * w; default: return 0.0375 * w; } }   // B_Y
- (CGPoint)smashRStickCenter { CGRect c = _layout.controls; return CGPointMake(CGRectGetMinX(c) + 0.918 * c.size.width, CGRectGetMinY(c) + 0.301 * c.size.height); }
- (CGRect)smashRectFor:(int)b { CGRect c = _layout.controls; CGFloat x = CGRectGetMinX(c), y = CGRectGetMinY(c), w = c.size.width, h = c.size.height;
    switch (b) { case B_L: return CGRectMake(x + 0.030 * w, y + 0.055 * h, 0.077 * w, 0.090 * h);
        case B_ZL: return CGRectMake(x + 0.125 * w, y + 0.055 * h, 0.099 * w, 0.090 * h);
        case B_ZR: return CGRectMake(x + 0.771 * w, y + 0.057 * h, 0.099 * w, 0.086 * h);
        default: return CGRectMake(x + 0.908 * w, y + 0.057 * h, 0.081 * w, 0.087 * h); } }   // B_R
- (CGFloat)smashRectDist:(CGRect)r point:(CGPoint)p { CGRect ri = CGRectInset(r, -8 * self.u, -8 * self.u);
    if (!CGRectContainsPoint(ri, p)) return CGFLOAT_MAX;
    return MAX(fabs(p.x - CGRectGetMidX(ri)) / (ri.size.width / 2), fabs(p.y - CGRectGetMidY(ri)) / (ri.size.height / 2)); }
- (CGRect)smashZoneRect:(int)z { CGRect c = _layout.controls; CGFloat x = CGRectGetMinX(c), y = CGRectGetMinY(c), w = c.size.width, h = c.size.height;
    switch (z) { case 0: { CGFloat s = 2 * 0.0375 * w; return CGRectMake(x + 0.8075 * w - s / 2, y + 0.8585 * h - s / 2, s, s); }   // S
        case 1: { CGFloat s = 2 * 0.0525 * w; return CGRectMake(x + 0.0555 * w - s / 2, y + 0.8405 * h - s / 2, s, s); }   // escudo
        case 2: { CGFloat s = 2 * 0.041 * w; return CGRectMake(x + 0.158 * w - s / 2, y + 0.855 * h - s / 2, s, s); }   // puno
        case 3: { CGFloat s = 2 * 0.042 * w; return CGRectMake(x + 0.261 * w - s / 2, y + 0.855 * h - s / 2, s, s); }   // mano
        default: return CGRectMake(x + 0.662 * w, y + 0.774 * h, 0.088 * w, 0.148 * h); } }   // pestana ZR
- (CGPoint)smashZoneCenter:(int)z { CGRect r = [self smashZoneRect:z]; return CGPointMake(CGRectGetMidX(r), CGRectGetMidY(r)); }
- (CGFloat)smashZoneR:(int)z { return [self smashZoneRect:z].size.width / 2; }
- (CGFloat)smashZoneDist:(int)z point:(CGPoint)p { return [self smashRectDist:[self smashZoneRect:z] point:p]; }
'''

ART_INIT = r'''        if (smashPad()) {
            for (int b = 0; b < B_N; b++) { UIImage *im = smashArtFor(b); if (im) { _art[b] = [CALayer layer]; _art[b].contents = (id)im.CGImage; _art[b].contentsGravity = kCAGravityResizeAspect; _art[b].hidden = YES; [_key[b] addSublayer:_art[b]]; } }
            _artDpad = [CALayer layer]; _artDpad.contents = (id)smashArtNamed(0).CGImage; _artDpad.contentsGravity = kCAGravityResizeAspect; _artDpad.hidden = YES; [_controls addSublayer:_artDpad];
            _artStickL = [CALayer layer]; _artStickL.contents = (id)smashArtNamed(1).CGImage; _artStickL.contentsGravity = kCAGravityResizeAspect; _artStickL.hidden = YES; [_controls insertSublayer:_artStickL below:_knob];
            _artStickR = [CALayer layer]; _artStickR.contents = (id)smashArtNamed(2).CGImage; _artStickR.contentsGravity = kCAGravityResizeAspect; _artStickR.hidden = YES; [_controls insertSublayer:_artStickR below:_knob2];
            for (int z = 0; z < 5; z++) { _zoneKey[z] = shape(_controls); _zoneKey[z].fillColor = k_zoneFill.CGColor; _zoneKey[z].hidden = YES; _zoneArt[z] = [CALayer layer]; _zoneArt[z].contents = (id)smashZoneArtFor(z).CGImage; _zoneArt[z].contentsGravity = kCAGravityResizeAspect; [_zoneKey[z] addSublayer:_zoneArt[z]]; }
        }
'''

LAYOUT_BLOCK = r'''    if ([self smashActive]) {
        for (int b = B_A; b <= B_Y; b++) { CGPoint c = [self facePos:b]; CGFloat r = [self smashFaceR:b]; setPath(_key[b], circlePath(c, r)); CGRect af = CGRectMake(c.x - r, c.y - r, 2 * r, 2 * r); _art[b].frame = b == B_A ? CGRectInset(af, -0.32 * r, -0.32 * r) : af; _label[b].hidden = YES; }
        static const int sh[4] = {B_ZL, B_L, B_ZR, B_R}; static const CGFloat asp[4] = {1.967, 1.525, 2.105, 1.672};
        for (int i = 0; i < 4; i++) { int b = sh[i]; CGRect rc = [self smashRectFor:b]; setPath(_key[b], CGPathCreateWithRoundedRect(rc, rc.size.height / 2, rc.size.height / 2, NULL)); _art[b].frame = smashFit(rc, asp[i]); _label[b].hidden = YES; }
        for (int i = 0; i < 2; i++) { int b = i ? B_MINUS : B_PLUS; _art[b].frame = [self pillRect:b]; _label[b].hidden = YES; }
        { CGPoint dc = self.dpadCenter; CGFloat dr = self.dpadR; _artDpad.frame = CGRectMake(dc.x - dr, dc.y - dr, 2 * dr, 2 * dr); }
        { CGPoint hc = self.stickHome; CGFloat hr = [self stickR:0]; _artStickL.frame = CGRectMake(hc.x - hr, hc.y - hr, 2 * hr, 2 * hr); }
        setPath(_ring2, circlePath([self smashRStickCenter], [self stickR:1]));
        { CGPoint rc2 = [self smashRStickCenter]; CGFloat rr = [self stickR:1]; _artStickR.frame = CGRectMake(rc2.x - rr, rc2.y - rr, 2 * rr, 2 * rr); }
        CGFloat k2 = [self stickR:1] * 0.5; _knob2.bounds = CGRectMake(0, 0, 2 * k2, 2 * k2); setPath(_knob2, circlePath(CGPointMake(k2, k2), k2));
        CAShapeLayer *kin2 = (CAShapeLayer *)_knob2.sublayers.firstObject; CGPathRef kip2 = circlePath(CGPointMake(k2, k2), k2 * 0.62); kin2.frame = _knob2.bounds; kin2.path = kip2; CGPathRelease(kip2);
        for (int z = 0; z < 5; z++) { CGRect rc = [self smashZoneRect:z]; if (z == 4) { setPath(_zoneKey[z], CGPathCreateWithRoundedRect(rc, rc.size.width * 0.44, rc.size.width * 0.44, NULL)); _zoneArt[z].frame = smashFit(rc, 1.071); } else { setPath(_zoneKey[z], circlePath(CGPointMake(CGRectGetMidX(rc), CGRectGetMidY(rc)), rc.size.width / 2)); _zoneArt[z].frame = rc; } }
    }
'''

GP = "dm/ios/Sources/DmGamepad.m"

patch(GP, [
    # colores nuevos: relleno de las zonas y del pomo derecho en reposo
    ("static UIColor *k_idle, *k_on, *k_line, *k_ringFill, *k_text, *k_textOn;",
     "static UIColor *k_idle, *k_on, *k_line, *k_ringFill, *k_text, *k_textOn, *k_smashFill, *k_zoneFill;"),
    ("k_ringFill = [UIColor colorWithWhite:1 alpha:0.06];",
     "k_ringFill = [UIColor colorWithWhite:1 alpha:0.06]; k_smashFill = [UIColor colorWithWhite:0 alpha:0.35]; k_zoneFill = [UIColor colorWithRed:0.45 green:0.30 blue:0.16 alpha:0.35];"),
    # gate con los sprites, tras la lista de teclas bloqueadas
    ("static const int k_btns[] = {B_ZL, B_L, B_ZR, B_R, B_MINUS, B_PLUS, B_LS, B_RS};   // keys locked at touch-down (L3 / R3 only in the 3D layout)",
     "static const int k_btns[] = {B_ZL, B_L, B_ZR, B_R, B_MINUS, B_PLUS, B_LS, B_RS};   // keys locked at touch-down (L3 / R3 only in the 3D layout)" + GATE),
    # capas nuevas: arte por tecla, zonas extra, arte de cruceta y sticks, stick derecho dibujado
    ("    CAShapeLayer *_key[B_N]; CATextLayer *_label[B_N];   // one layer per key",
     """    CAShapeLayer *_key[B_N]; CATextLayer *_label[B_N];   // one layer per key
    CALayer *_art[B_N];   // medallones del usuario sobre cada tecla (solo Smash)
    CAShapeLayer *_zoneKey[5]; CALayer *_zoneArt[5]; BOOL _zoneOn[5];   // zonas extra (solo Smash)
    CALayer *_artDpad, *_artStickL, *_artStickR;   // arte de la cruceta y de los sticks (solo Smash)
    CAShapeLayer *_ring2, *_knob2;   // stick derecho dibujado (solo en el modo Smash)"""),
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
    # creacion del arte tras crear las teclas (las capas _key ya existen ahi)
    ("""        for (int b = 0; b < B_N; b++) {
            _key[b] = shape(_controls);
            if (names[b]) _label[b] = label(_key[b], names[b]);   // the D-pad arms carry no label
        }""",
     """        for (int b = 0; b < B_N; b++) {
            _key[b] = shape(_controls);
            if (names[b]) _label[b] = label(_key[b], names[b]);   // the D-pad arms carry no label
        }
""" + ART_INIT),
    # visibilidad: en Smash se ve todo en 2D y 3D, menos L3/R3 (sin uso en el juego)
    ("""    for (int b = 0; b < B_N; b++) _key[b].hidden = _tap || (fullOnly(b) && !_full);
    _ring.hidden = _knob.hidden = _tap;""",
     """    BOOL sm = [self smashActive];
    for (int b = 0; b < B_N; b++) { _key[b].hidden = _tap || (sm ? (b == B_LS || b == B_RS) : (fullOnly(b) && !_full)); if (_art[b]) _art[b].hidden = _key[b].hidden; }
    _ring.hidden = _knob.hidden = _tap;
    _ring2.hidden = _knob2.hidden = _tap || !sm;
    if (_artDpad) _artDpad.hidden = _tap || !sm;
    if (_artStickL) _artStickL.hidden = _tap;
    if (_artStickR) _artStickR.hidden = _tap || !sm;
    for (int z = 0; z < 5; z++) if (_zoneKey[z]) _zoneKey[z].hidden = _tap || !sm;"""),
    # botones de cara en su sitio de la imagen (no en diamante)
    ("- (CGPoint)facePos:(int)b { CGPoint c = self.faceCenter; CGFloat g = self.faceGap;",
     "- (CGPoint)facePos:(int)b { if ([self smashActive]) return [self smashFaceCenter:b]; CGPoint c = self.faceCenter; CGFloat g = self.faceGap;"),
    # stick izquierdo en su sitio de la imagen
    ("- (CGPoint)stickHome {\n    if (self.portraitControls) {",
     "- (CGPoint)stickHome {\n    if ([self smashActive]) { CGRect c = _layout.controls; return CGPointMake(CGRectGetMinX(c) + 0.1505 * c.size.width, CGRectGetMinY(c) + 0.601 * c.size.height); }\n    if (self.portraitControls) {"),
    ("- (CGFloat)stickR:(int)i { return (i ? K_RSTICK_R : K_STICK_R) * self.u; }",
     "- (CGFloat)stickR:(int)i { if ([self smashActive]) return (i ? 0.059 : 0.0605) * _layout.controls.size.width; return (i ? K_RSTICK_R : K_STICK_R) * self.u; }"),
    # cruceta en su sitio de la imagen
    ("- (CGPoint)dpadCenter {\n    if (self.portraitControls) {",
     "- (CGPoint)dpadCenter {\n    if ([self smashActive]) { CGRect c = _layout.controls; return CGPointMake(CGRectGetMinX(c) + 0.3035 * c.size.width, CGRectGetMinY(c) + 0.609 * c.size.height); }\n    if (self.portraitControls) {"),
    ("- (CGFloat)dpadR { return K_DPAD_R * self.u; }",
     "- (CGFloat)dpadR { return [self smashActive] ? 0.0745 * _layout.controls.size.width : K_DPAD_R * self.u; }"),
    # + / - como medallones redondos en su sitio (la tuerca queda entre ellos)
    ("- (CGRect)pillRect:(int)b { CGRect s = self.safe;",
     """- (CGRect)pillRect:(int)b { if ([self smashActive]) { CGRect c = _layout.controls; CGFloat side = 0.056 * c.size.width; CGPoint ctr = CGPointMake(CGRectGetMinX(c) + (b == B_PLUS ? 0.430 : 0.581) * c.size.width, CGRectGetMinY(c) + (b == B_PLUS ? 0.1135 : 0.113) * c.size.height); return CGRectMake(ctr.x - side / 2, ctr.y - side / 2, side, side); } CGRect s = self.safe;"""),
    # metodos auxiliares, antes de menuDistance (la tuerquita NO se toca)
    ("- (CGFloat)menuDistance:(CGPoint)p {",
     HELPERS + "- (CGFloat)menuDistance:(CGPoint)p {"),
    # hit de hombros por su pastilla y de las zonas extra con el mismo bit
    ("""- (CGFloat)buttonDistance:(int)b point:(CGPoint)p {
    CGFloat u = self.u;""",
     """- (CGFloat)buttonDistance:(int)b point:(CGPoint)p {
    CGFloat u = self.u;
    if ([self smashActive]) {
        if (isDrop(b)) { CGFloat d = [self smashRectDist:[self smashRectFor:b] point:p];
            if (b == B_L) d = MIN(d, [self smashZoneDist:1 point:p]);
            if (b == B_ZL) d = MIN(d, [self smashZoneDist:3 point:p]);
            if (b == B_ZR) d = MIN(d, [self smashZoneDist:4 point:p]);
            return d; }
        if (isClick(b)) return CGFLOAT_MAX;
    }"""),
    # L3/R3 tampoco se pueden pulsar en Smash (están ocultos)
    ("        if (fullOnly(b) && !_full) continue;",
     "        if ((fullOnly(b) && !_full) || ([self smashActive] && isClick(b))) continue;"),
    # faceAt con los radios de cada boton y las zonas de A (puno) y B (S)
    ("""- (uint64_t)faceAt:(CGPoint)p {   // keys under the finger in the diamond (between two keys both count)
    uint64_t m = 0; CGFloat r = self.faceHitR;""",
     """- (uint64_t)faceAt:(CGPoint)p {   // keys under the finger in the diamond (between two keys both count)
    if ([self smashActive]) { uint64_t m = 0;
        for (int b = B_A; b <= B_Y; b++) if (dist(p, [self facePos:b]) <= [self smashFaceR:b] * 1.12) m |= 1ull << b;
        if (dist(p, [self smashZoneCenter:2]) <= [self smashZoneR:2] * 1.15) m |= 1ull << B_A;
        if (dist(p, [self smashZoneCenter:0]) <= [self smashZoneR:0] * 1.15) m |= 1ull << B_B;
        return m; }
    uint64_t m = 0; CGFloat r = self.faceHitR;"""),
    # controlAt: cara, cruceta y stick derecho fijo reclaman tambien en 2D
    ("    if (dist(p, self.faceCenter) / (self.faceGap + MAX(self.faceR * 1.6, self.faceHitR)) <= 1) return YES;",
     "    if ([self smashActive] && [self faceAt:p]) return YES;\n    if (dist(p, self.faceCenter) / (self.faceGap + MAX(self.faceR * 1.6, self.faceHitR)) <= 1) return YES;"),
    ("    if (_full && dist(p, self.dpadCenter) / MAX(self.dpadR * K_DPAD_GRAB, _layout.separated ? 22 : 0) < 1) return YES;",
     "    if ((_full || [self smashActive]) && dist(p, self.dpadCenter) / MAX(self.dpadR * K_DPAD_GRAB, _layout.separated ? 22 : 0) < 1) return YES;"),
    ("    return _full && !_stick[1] && [self inRightArea:p];",
     "    if ([self smashActive]) return !_stick[1] && dist(p, [self smashRStickCenter]) / MAX([self stickR:1] * K_STICK_GRAB, _layout.separated ? 22 : 0) < 1;\n    return _full && !_stick[1] && [self inRightArea:p];"),
    # touchesBegan: la cara reclama si faceAt acierta; la cruceta tambien en 2D
    ("        CGFloat f = dist(p, self.faceCenter) / (self.faceGap + MAX(self.faceR * 1.6, self.faceHitR)); if (f <= best) { best = f; kind = C_FACE; }",
     "        if ([self smashActive] && [self faceAt:p]) { best = 0; kind = C_FACE; }\n        CGFloat f = dist(p, self.faceCenter) / (self.faceGap + MAX(self.faceR * 1.6, self.faceHitR)); if (f <= best) { best = f; kind = C_FACE; }"),
    ("        if (_full) { CGFloat d = dist(p, self.dpadCenter) / MAX(self.dpadR * K_DPAD_GRAB, _layout.separated ? 22 : 0); if (d < best) { best = d; kind = C_DPAD; } }",
     "        if (_full || [self smashActive]) { CGFloat d = dist(p, self.dpadCenter) / MAX(self.dpadR * K_DPAD_GRAB, _layout.separated ? 22 : 0); if (d < best) { best = d; kind = C_DPAD; } }"),
    # touchesBegan: el stick derecho se reclama desde su anillo fijo; el flotante queda para el resto
    ("        if (kind == C_NONE && _full && !_stick[1] && [self inRightArea:p]) { kind = C_STICK; idx = 1; _rCentre = p; }   // the right stick: centred where the touch lands",
     "        if (kind == C_NONE && [self smashActive] && !_stick[1]) { CGFloat s = dist(p, [self smashRStickCenter]) / MAX([self stickR:1] * K_STICK_GRAB, _layout.separated ? 22 : 0); if (s <= 1) { kind = C_STICK; idx = 1; _rCentre = [self smashRStickCenter]; } }\n        if (kind == C_NONE && _full && !_stick[1] && ![self smashActive] && [self inRightArea:p]) { kind = C_STICK; idx = 1; _rCentre = p; }   // the right stick: centred where the touch lands"),
    # touchesMoved: en Smash el centro del stick derecho no sigue al dedo (es fijo)
    ("            if ((v >> 8) == 1) { CGFloat d = dist(p, _rCentre), R = [self stickR:1];   // the right stick's centre follows a finger past its radius, so turning back responds at once",
     "            if ((v >> 8) == 1 && ![self smashActive]) { CGFloat d = dist(p, _rCentre), R = [self stickR:1];   // the right stick's centre follows a finger past its radius, so turning back responds at once"),
    # recompute: refrescar también mientras se usa el stick derecho (su pomo se mueve)
    ("    BOOL stick = _stick[0] != nil;   // only the left stick is drawn: the right one needs no refresh",
     "    BOOL stick = _stick[0] != nil || ([self smashActive] && _stick[1] != nil);   // only the left stick is drawn: the right one needs no refresh (en Smash si: tiene anillo propio)"),
    # refresh: estado por zona (cada zona se enciende solo si se pulsa ella)
    ("""- (void)refresh {   // pressed state → fill, sticks → knob position
    uint64_t all = _faceBits | _dpadBits | _btnBits;""",
     """- (void)refresh {   // pressed state → fill, sticks → knob position
    uint64_t all = _faceBits | _dpadBits | _btnBits;
    BOOL sm = [self smashActive];
    if (sm) { for (int z = 0; z < 5; z++) _zoneOn[z] = NO;
        for (UITouch *t in _owner) { uint64_t v = [_owner objectForKey:t].unsignedLongLongValue; int c = (int)(v & 0xff); CGPoint p = [t locationInView:self];
            if (c == C_BTN) { int bit = (int)(v >> 8); for (int z = 0; z < 5; z++) if (k_zoneBit[z] == bit && [self smashZoneDist:z point:p] <= 1) _zoneOn[z] = YES; }
            else if (c == C_FACE) { uint64_t m = [_faceOf objectForKey:t].unsignedLongLongValue;
                if ((m >> B_B) & 1) { if ([self smashZoneDist:0 point:p] <= 1) _zoneOn[0] = YES; }
                if ((m >> B_A) & 1) { if ([self smashZoneDist:2 point:p] <= 1) _zoneOn[2] = YES; } } } }"""),
    # refresh: el arte se encoge un poco al pulsar (la pulsacion se nota sobre el medallon)
    ("        _key[b].fillColor = (on ? k_on : k_idle).CGColor; _label[b].foregroundColor = (on ? k_textOn : k_text).CGColor; }",
     "        _key[b].fillColor = (on ? k_on : k_idle).CGColor; _label[b].foregroundColor = (on ? k_textOn : k_text).CGColor; if (_art[b]) _art[b].transform = (sm && on) ? CATransform3DMakeScale(0.93, 0.93, 1) : CATransform3DIdentity; }"),
    # refresh: zonas y pomo del stick derecho
    ("    CGPoint h = self.stickHome, o = [self knobOffset:0];",
     """    if (_ring2) { _ring2.hidden = _tap || !sm; _knob2.hidden = _tap || !sm; if (sm) { CGPoint rc = [self smashRStickCenter], ro = [self knobOffset:1]; _knob2.position = CGPointMake(rc.x + ro.x, rc.y + ro.y); _knob2.fillColor = (_stick[1] ? k_on : k_smashFill).CGColor; } }
    if (sm) for (int z = 0; z < 5; z++) { _zoneKey[z].fillColor = (_zoneOn[z] ? k_on : k_zoneFill).CGColor; _zoneArt[z].transform = _zoneOn[z] ? CATransform3DMakeScale(0.93, 0.93, 1) : CATransform3DIdentity; }
    CGPoint h = self.stickHome, o = [self knobOffset:0];"""),
    # dibujo Smash al final de layoutSubviews
    ("    [CATransaction commit];\n    [self refresh];\n}",
     LAYOUT_BLOCK + "    [CATransaction commit];\n    [self refresh];\n}"),
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
print("Parche aplicado: lanzador en español + controles bronce para Smash controles mobiles.")
