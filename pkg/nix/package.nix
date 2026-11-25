# The nixpkgs expression: callPackage ./package.nix { }
{
  lib,
  stdenvNoCC,
  fetchurl,
  makeWrapper,
  python3,
  git,
}:

stdenvNoCC.mkDerivation (finalAttrs: {
  pname = "standards-sync";
  version = "@VERSION@";

  src = fetchurl {
    url = "@URL@";
    hash = "@SRI@";
  };

  nativeBuildInputs = [ makeWrapper ];
  buildInputs = [ python3 ];

  installPhase = ''
    runHook preInstall
    mkdir -p $out
    cp -r bin share $out/
    wrapProgram $out/bin/standards-sync --prefix PATH : ${lib.makeBinPath [ git ]}
    runHook postInstall
  '';

  meta = {
    description = "Keep the code standards in sync without losing edits";
    homepage = "https://github.com/sebastienrousseau/standards";
    license = with lib.licenses; [
      asl20
      mit
    ];
    mainProgram = "standards-sync";
    platforms = lib.platforms.unix;
  };
})
