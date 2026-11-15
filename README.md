# smash-build-ci

Repo público SOLO de compilación para la build privada de Super Smash Bros.
Ultimate del usuario (vía nxnative, upstream seedds/nxnative).

Contiene únicamente:
- `.github/workflows/build.yml` — el flujo de compilación en macOS.
- `tools/parche_smash.py` — traducción del lanzador DmIOS al español,
  ajustes de rendimiento por defecto y controles táctiles rediseñados
  (solo para este juego).

No contiene ningún archivo del juego ni claves: el flujo los descarga de la
release privada `smash-game` del repo privado `smash-build` con un token
guardado como secreto del repo (se pone para compilar y se borra después),
y sube el resultado a la release privada `smash-ipa-v2` de ese mismo repo.
